/* Comptage hors-ligne (F3).
 *
 * Le comptage se fait en réserve ou en chambre froide : le réseau tombe sans
 * prévenir et une session perdue à la reconnexion détruit la confiance en un
 * seul incident. Chaque zone enregistrée part au serveur si le réseau est là,
 * sinon dans une file locale rejouée à la reconnexion.
 *
 * L'heure de saisie part avec chaque ligne : c'est elle, pas l'heure
 * d'arrivée au serveur, qui départage deux appareils sur la même session.
 */
(function () {
  const root = document.querySelector("[data-counting-session]");
  if (!root) return;

  const sessionId = root.dataset.countingSession;
  const revision = root.dataset.countRevision || "";
  const QUEUE_KEY = `comptage-file-${sessionId}`;
  const banner = document.querySelector("[data-offline-banner]");

  const readQueue = () => {
    try {
      return JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
    } catch (_) {
      return [];
    }
  };

  const writeQueue = (queue) => {
    try {
      localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    } catch (_) {
      /* stockage plein ou refusé : on continue en ligne uniquement */
    }
  };

  const setBanner = (text, tone) => {
    if (!banner) return;
    banner.textContent = text || "";
    banner.hidden = !text;
    banner.className = text
      ? `mb-3 rounded border px-3 py-2 text-sm ${
          tone === "error" ? "flash-error" : tone === "ok" ? "flash-success"
          : "border-amber-300 bg-amber-50 text-amber-800"
        }`
      : "";
  };

  const refreshBanner = () => {
    const pending = readQueue().length;
    if (!navigator.onLine) {
      setBanner(
        pending
          ? `Hors ligne — ${pending} ligne(s) en attente, elles partiront à la reconnexion.`
          : "Hors ligne — vous pouvez continuer le comptage, tout est gardé sur l'appareil.",
        "warn"
      );
    } else if (pending) {
      setBanner(`${pending} ligne(s) en attente d'envoi…`, "warn");
    } else {
      setBanner("", null);
    }
  };

  /** Lignes saisies d'un formulaire de zone. */
  const collect = (form) => {
    const entries = [];
    form.querySelectorAll("[data-count-row]").forEach((row) => {
      const input = row.querySelector(".count-input");
      if (!input || input.value.trim() === "") return;
      const quantity = parseFloat(input.value.replace(",", "."));
      if (Number.isNaN(quantity)) return;
      const reason = row.querySelector("select[name^='reason_']");
      entries.push({
        line_id: Number(input.name.replace("count_", "")),
        counted_quantity: quantity,
        variance_reason: reason ? reason.value : "",
        entered_at: Date.now(),
      });
    });
    return entries;
  };

  const reportConflicts = (conflicts) => {
    if (!conflicts || !conflicts.length) return false;
    const details = conflicts
      .map((c) => `${c.ingredient} (valeur conservée : ${c.kept})`)
      .join(", ");
    setBanner(
      `${conflicts.length} ligne(s) modifiée(s) depuis un autre appareil, votre saisie plus ancienne n'a pas été appliquée : ${details}`,
      "error"
    );
    return true;
  };

  /* Recharge la page : la liste affichée ne correspond plus au serveur. La
   * file est vide à ce stade, on ne perd donc aucune saisie. */
  const reloadStale = (message) => {
    setBanner(message, "warn");
    setTimeout(() => window.location.reload(), 2500);
  };

  /** Envoie la file au serveur. Renvoie true si elle est vidée. */
  const flush = async () => {
    const queue = readQueue();
    if (!queue.length) return true;
    let response;
    try {
      response = await fetch(`/counting/${sessionId}/sync`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entries: queue, revision: revision }),
      });
    } catch (_) {
      return false; // toujours hors ligne : la file reste intacte
    }

    let result = null;
    try {
      result = await response.json();
    } catch (_) {
      result = null;
    }

    if (response.status === 409 && result && result.closed) {
      // Comptage clos ailleurs : rien n'a été écrit. On garde la file pour que
      // la saisie reste consultable, et on dit clairement ce qui s'est passé.
      setBanner(result.error, "error");
      return false;
    }
    if (!response.ok) return false;

    writeQueue([]);
    if (result && result.stale) {
      reloadStale("Liste mise à jour depuis un autre appareil — rechargement de la page.");
      return true;
    }
    if (!reportConflicts(result && result.conflicts)) {
      const applied = result ? result.applied : 0;
      setBanner(`Comptage synchronisé — ${applied} ligne(s) enregistrée(s).`, "ok");
      setTimeout(refreshBanner, 6000);
    }
    return true;
  };

  document.querySelectorAll("form[data-zone-form]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      // Horodatage de saisie pour l'envoi classique (formulaire en ligne).
      const stamp = Date.now();
      form.querySelectorAll("[data-count-row] .count-input").forEach((input) => {
        const lineId = input.name.replace("count_", "");
        let hidden = form.querySelector(`input[name="entered_at_${lineId}"]`);
        if (!hidden) {
          hidden = document.createElement("input");
          hidden.type = "hidden";
          hidden.name = `entered_at_${lineId}`;
          form.appendChild(hidden);
        }
        hidden.value = String(stamp);
      });

      if (navigator.onLine) return; // envoi normal

      // Hors ligne : on garde la saisie et on reste sur la page.
      event.preventDefault();
      const queue = readQueue().concat(collect(form));
      writeQueue(queue);
      form.querySelectorAll("[data-count-row]").forEach((row) => {
        row.dataset.pending = "1";
      });
      refreshBanner();
    });
  });

  const completeForm = document.querySelector("form[data-complete-form]");
  if (completeForm) {
    completeForm.addEventListener("submit", (event) => {
      let hidden = completeForm.querySelector('input[name="ended_at"]');
      if (!hidden) {
        hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "ended_at";
        completeForm.appendChild(hidden);
      }
      hidden.value = String(Date.now()); // durée juste même si l'envoi part plus tard
      if (!navigator.onLine) {
        event.preventDefault();
        setBanner(
          "Hors ligne : terminez le comptage une fois le réseau revenu, vos saisies sont gardées.",
          "warn"
        );
      }
    });
  }

  window.addEventListener("online", () => {
    refreshBanner();
    flush();
  });
  window.addEventListener("offline", refreshBanner);

  refreshBanner();
  if (navigator.onLine) flush();
})();
