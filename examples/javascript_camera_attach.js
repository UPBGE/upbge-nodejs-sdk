// Camera attach: posição da câmera calculada a partir da posição do cubo
// Setup: no Cubo (ou no objeto a ser seguido), ligue um Always ao controller com este script.

const scene = bge.logic.getCurrentScene();
const cont = bge.logic.getCurrentController();
const target = cont.owner;
const cam = scene.getObject("Camera");

if (!cam || !target) return;

const pos = target.position;

// Offset: distância da câmera em relação ao cubo (em metros, eixos mundiais do Blender)
// [X, Y, Z] = quanto a câmera fica à direita/esquerda, atrás/na frente, abaixo/acima do cubo
//   X > 0 = câmera à direita do cubo; X < 0 = à esquerda
//   Y > 0 = câmera atrás do cubo (em +Y); Y < 0 = na frente
//   Z > 0 = câmera acima do cubo; Z < 0 = abaixo
const offset = [0, 4, 3];
cam.position = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];

// Ponto para onde a câmera olha (um pouco acima do cubo)
const lookHeight = 1.5;  // quanto acima do cubo (Z); aumentar = câmera olha mais para cima
const look = [pos[0], pos[1], pos[2] + lookHeight];

const camPos = cam.position;
let dx = look[0] - camPos[0], dy = look[1] - camPos[1], dz = look[2] - camPos[2];
const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
if (len > 1e-6) {
  dx /= len; dy /= len; dz /= len;
  // Rotação: X = pitch (cima/baixo), Y = 0, Z = heading (esquerda/direita)
  // pitchOffset: positivo = câmera mais para cima; negativo = mais para baixo (em radianos)
  const pitchOffset = 0.6;  // se ainda apontar pra baixo, aumente (ex.: 0.7)
  cam.rotation = [Math.asin(dz) + pitchOffset, 0, Math.atan2(dx, dy)];
}
