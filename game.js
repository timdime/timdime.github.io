const canvas = document.getElementById('dimeGame');
const ctx = canvas.getContext('2d');

const dimeImage = new Image();
dimeImage.src = 'images/dime-sprite.png';

let dimes = [];
let score = 0;

function spawnDime() {
  const dime = {
    x: Math.random() * (canvas.width - 50),
    y: -50,
    speed: 2 + Math.random() * 3,
    size: 50
  };
  dimes.push(dime);
}

function update() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  dimes.forEach((dime, index) => {
    dime.y += dime.speed;
    ctx.drawImage(dimeImage, dime.x, dime.y, dime.size, dime.size);

    if (dime.y > canvas.height) {
      dimes.splice(index, 1);
    }
  });
  requestAnimationFrame(update);
}

canvas.addEventListener('click', (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  dimes.forEach((dime, index) => {
    if (x > dime.x && x < dime.x + dime.size && y > dime.y && y < dime.y + dime.size) {
      dimes.splice(index, 1);
      score++;
      console.log('Score:', score);
    }
  });
});

setInterval(spawnDime, 800);
update();
