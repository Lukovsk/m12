<script>
    // 1. REGISTRA O COMPONENTE CUSTOMIZADO 'troca-video'
    AFRAME.registerComponent('troca-video', {
        // 2. INICIALIZAÇÃO: Onde o componente é anexado pela primeira vez
        init: function () {
            // Obter a lista de IDs de vídeo da tag auxiliar no assets
            const videoListElement = document.getElementById('video-list');
            const videoIds = videoListElement.getAttribute('data-videos').split(',');
            
            this.videoIds = videoIds; // Array de IDs de vídeos
            this.currentVideoIndex = 0; // Começa no primeiro vídeo (0)
            this.videoElement = null; // Para guardar a referência ao elemento do vídeo
            
            // Referência ao elemento da TV ao qual este componente está anexado
            const el = this.el; 
            
            // 3. O EVENTO DE INTERAÇÃO (Clique/Tap)
            el.addEventListener('click', () => {
                // Avança para o próximo vídeo, voltando ao 0 se chegar ao fim
                this.currentVideoIndex = (this.currentVideoIndex + 1) % this.videoIds.length;
                
                const nextVideoId = this.videoIds[this.currentVideoIndex];
                
                // 4. ATUALIZAÇÃO DA TEXTURA
                
                // 4.1. Para o vídeo anterior, se houver
                if (this.videoElement) {
                    this.videoElement.pause();
                }

                // 4.2. Pega o novo elemento de vídeo
                this.videoElement = document.getElementById(nextVideoId);
                
                // 4.3. Aplica a nova textura à tela da TV
                el.setAttribute('material', 'src', `#${nextVideoId}`);
                
                // 4.4. Inicia o novo vídeo
                this.videoElement.play();
                console.log(`Trocando para: ${nextVideoId}`);
            });

            // O A-Frame usa um mecanismo de Raycaster (raio de luz para "selecionar" o objeto)
            // É importante mudar o cursor para indicar que o objeto é clicável
            el.addEventListener('mouseenter', function () {
                document.body.style.cursor = 'pointer'; // Muda o cursor ao passar o mouse
            });

            el.addEventListener('mouseleave', function () {
                document.body.style.cursor = 'default'; // Volta ao cursor padrão
            });
        }
    });
</script>