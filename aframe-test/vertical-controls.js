AFRAME.registerComponent("vertical-controls", {
  schema: {
    speed: { type: "number", default: 0.1 }, // Velocidade de subida/descida por frame
  },

  init: function () {
    this.el.sceneEl.addEventListener("keydown", this.handleKeyDown.bind(this));
    this.el.sceneEl.addEventListener("keyup", this.handleKeyUp.bind(this));

    this.movingUp = false;
    this.movingDown = false;
  },

  handleKeyDown: function (evt) {
    // Tecla SPACE (código 32)
    if (evt.keyCode === 32) {
      this.movingUp = true;
    }
    // Tecla SHIFT (código 16)
    if (evt.keyCode === 16) {
      this.movingDown = true;
    }
  },

  handleKeyUp: function (evt) {
    if (evt.keyCode === 32) {
      this.movingUp = false;
    }
    if (evt.keyCode === 16) {
      this.movingDown = false;
    }
  },

  tick: function () {
    var position = this.el.getAttribute("position");
    var speed = this.data.speed;

    if (this.movingUp) {
      position.y += speed;
    }
    if (this.movingDown) {
      position.y -= speed;
    }

    // Aplica a nova posição, garantindo que o chão não seja atravessado
    if (position.y < 0.1) {
      position.y = 0.1;
    }

    this.el.setAttribute("position", position);
  },
});
