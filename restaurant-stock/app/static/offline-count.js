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
    // Le fond de statut porte le sens : pas d'icône décorative, et l'attente
    // de synchronisation n'emprunte pas les couleurs de l'erreur.
    banner.className = text
      ? `mb-3 rounded border px-3 py-2 text-base ${
          tone === "error" ? "flash-error" : tone === "ok" ? "flash-success"
          : "border-trait bg-appui text-encre"
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
      const input = row.querySelector("input[name^='count_']");
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

  /* --- Retour visible sur place ----------------------------------------
   * Enregistrer une zone ne recharge plus la page : le champ passe en état
   * confirmé, la zone dit « enregistré », l'avancement suit. Un rechargement
   * silencieux ne dit rien au doigt qui vient d'appuyer.
   */
  const marquerConfirme = (form) => {
    form.querySelectorAll("[data-count-row] [data-champ]").forEach((champ) => {
      const input = champ.querySelector("input[name^='count_']");
      if (input && input.value.trim() !== "") champ.dataset.etat = "confirme";
    });
  };

  const majAvancement = () => {
    const compteur = document.querySelector("[data-avancement]");
    const jauge = document.querySelector("[data-jauge]");
    if (!compteur) return;
    const total = Number(compteur.dataset.total) || 0;
    const faits = document.querySelectorAll('[data-champ][data-etat="confirme"]').length;
    compteur.innerHTML = `${faits}<span class="text-gris">/${total}</span>`;
    if (jauge) jauge.style.width = total ? `${(faits / total) * 100}%` : "0%";
  };

  const majZone = (form, confirmation) => {
    const bloc = form.closest("details[data-zone]");
    if (!bloc) return;
    const etat = bloc.querySelector("[data-zone-etat]");
    if (!etat) return;
    const lignes = bloc.querySelectorAll("[data-count-row]").length;
    const faits = bloc.querySelectorAll('[data-champ][data-etat="confirme"]').length;
    const repos = () => {
      if (faits >= lignes) {
        etat.textContent = "terminé";
        etat.classList.add("text-valide", "font-semibold");
      } else {
        etat.innerHTML = `<span class="nombre">${faits}/${lignes}</span>`;
        etat.classList.remove("text-valide", "font-semibold");
      }
    };
    if (confirmation) {
      etat.textContent = "enregistré";
      etat.classList.add("text-valide", "font-semibold");
      setTimeout(repos, 2400); // confirmation brève, puis retour à l'état réel
    } else {
      repos();
    }
  };

  /** Envoi d'une zone sans quitter la page. Renvoie false si le réseau a
   *  lâché entre-temps, pour retomber sur la file locale. */
  const envoyerZone = async (form) => {
    let response;
    try {
      response = await fetch(`/counting/${sessionId}/sync`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entries: collect(form), revision: revision }),
      });
    } catch (_) {
      return false;
    }
    let result = null;
    try {
      result = await response.json();
    } catch (_) {
      result = null;
    }
    if (response.status === 409 && result && result.closed) {
      setBanner(result.error, "error");
      return true; // rien à mettre en file : le comptage est clos
    }
    if (!response.ok) return false;
    if (result && result.stale) {
      reloadStale("La liste a changé depuis un autre appareil, la page se recharge.");
      return true;
    }
    if (reportConflicts(result && result.conflicts)) return true;
    marquerConfirme(form);
    majZone(form, true);
    majAvancement();
    return true;
  };

  document.querySelectorAll("form[data-zone-form]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      // Horodatage de saisie pour l'envoi classique (formulaire sans script).
      const stamp = Date.now();
      form.querySelectorAll("[data-count-row] input[name^='count_']").forEach((input) => {
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

      // On ne quitte jamais la page : en ligne on envoie et on confirme sur
      // place, hors ligne on met en file. Sans script, le `<form>` classique
      // continue de fonctionner tel quel.
      event.preventDefault();

      if (navigator.onLine) {
        envoyerZone(form).then((envoye) => {
          if (envoye) return;
          // Le réseau a lâché pendant l'envoi : la saisie part en file.
          writeQueue(readQueue().concat(collect(form)));
          refreshBanner();
        });
        return;
      }

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
