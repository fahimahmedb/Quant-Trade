// Spatial placement is presentation, never role inference or business authority.
export const ZONES=Object.freeze([
 {id:'research',name:'MECHANISMS',sub:'RESEARCH / 01',x:-9.8,y:.8,z:-6,angle:.38,type:'library'},
 {id:'documents',name:'DOCUMENTS',sub:'EVENT INTELLIGENCE / 02',x:-10,y:3.8,z:-13,angle:0,type:'archive'},
 {id:'fundamental',name:'FUNDAMENTAL',sub:'RESEARCH / 03',x:-3.2,y:.8,z:-14,angle:0,type:'seminar'},
 {id:'flows',name:'FLOWS / REGULATORY',sub:'CONTEXT / 04',x:5,y:.8,z:-13,angle:-.15,type:'maps'},
 {id:'data',name:'DATA / EVIDENCE',sub:'PROVENANCE / 05',x:-10,y:.8,z:1.5,angle:.65,type:'evidence'},
 {id:'validation',name:'VALIDATION',sub:'RED TEAM / 06',x:10.5,y:.8,z:-5,angle:-.55,type:'validation'},
 {id:'decay',name:'EDGE ARCHAEOLOGY',sub:'MEMORY / DECAY / 07',x:-12,y:.3,z:8,angle:.6,type:'archive'},
 {id:'implement',name:'IMPLEMENTABILITY',sub:'ENGINEERING / 08',x:11.5,y:.3,z:6,angle:-.75,type:'engineering'},
 {id:'experiment',name:'EXPERIMENT SYSTEMS',sub:'INFRASTRUCTURE / 09',x:13,y:.8,z:-12,angle:-.5,type:'racks'},
 {id:'identity',name:'ECONOMIC IDENTITY',sub:'INTEGRATION / 10',x:4.3,y:.3,z:6.5,angle:-.4,type:'identity'},
 {id:'portfolio',name:'PORTFOLIO',sub:'INTEGRATION / 11',x:-3.5,y:.3,z:9.5,angle:.18,type:'portfolio'},
]);
export const ROLE_STATIONS=Object.freeze({
 researcher:{position:[-9.36,.8,-4.88],angle:.38},
 builder:{position:[10.68,.3,6.88],angle:-.75},
 data:{position:[-9.27,.8,2.45],angle:.65},
 auditor:{position:[9.87,.8,-3.98],angle:-.55},
 manager:{position:[-3.29,.3,10.68],angle:.18},
 worker:{position:[3.83,.3,7.61],angle:-.4},
});
