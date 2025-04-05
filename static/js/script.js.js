document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips y popovers de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configurar carruseles
    var mainCarousel = document.getElementById('mainCarousel');
    if (mainCarousel) {
        var carousel = new bootstrap.Carousel(mainCarousel, {
            interval: 5000,
            wrap: true,
            keyboard: true
        });
    }

    var newsCarousel = document.getElementById('newsCarousel');
    if (newsCarousel) {
        var newsCarouselInstance = new bootstrap.Carousel(newsCarousel, {
            interval: 5000,
            wrap: true,
            keyboard: true
        });
    }

    // Inicializar el calendario
    initCalendar();

    // Manejar clics en items que abren modales
    document.querySelectorAll('[data-modal]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            var modalId = this.getAttribute('data-modal');
            var modalElement = document.getElementById(modalId);
            
            if (modalElement) {
                var modal = new bootstrap.Modal(modalElement);
                modal.show();
            } else {
                console.error('Modal no encontrado: ' + modalId);
            }
        });
    });

    // Manejar cambios en el número de asistentes
    var numAsistentesSelect = document.getElementById('num-asistentes');
    if (numAsistentesSelect) {
        numAsistentesSelect.addEventListener('change', function() {
            var num = parseInt(this.value);
            var container = document.getElementById('asistentes-container');
            container.innerHTML = '';
            
            for (var i = 1; i <= num; i++) {
                var asistenteForm = document.createElement('div');
                asistenteForm.className = 'asistente-form mb-3';
                
                asistenteForm.innerHTML = `
                    <h6>Asistente ${i}</h6>
                    <div class="mb-2">
                        <label for="asistente-${i}-nombre" class="form-label">Nombre completo</label>
                        <input type="text" class="form-control" id="asistente-${i}-nombre" required>
                    </div>
                `;
                
                container.appendChild(asistenteForm);
            }
        });
    }

    // Manejar envío de formulario de inscripción
    var inscripcionForm = document.getElementById('inscripcion-form');
    if (inscripcionForm) {
        inscripcionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!this.checkValidity()) {
                e.stopPropagation();
                this.classList.add('was-validated');
                return;
            }
            
            // Aquí iría la lógica para enviar los datos al servidor y procesar el pago
            // Para este ejemplo, simplemente simulamos una confirmación
            alert('Inscripción procesada correctamente. Recibirás un correo de confirmación.');
            
            // Cerrar el modal después de procesar
            var inscripcionModal = bootstrap.Modal.getInstance(document.getElementById('inscripcion-modal'));
            inscripcionModal.hide();
        });
    }

    // Manejar envío de formulario de registro
    var registroForm = document.getElementById('registro-form');
    if (registroForm) {
        registroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!this.checkValidity()) {
                e.stopPropagation();
                this.classList.add('was-validated');
                return;
            }
            
            // Aquí iría la lógica para enviar los datos al servidor
            // Luego redirigir a la página de amigos de Torreciudad
            alert('Registro enviado correctamente. Serás redirigido a la página de Amigos de Torreciudad.');
            window.open('https://torreciudad.org/amigos-de-torreciudad/', '_blank');
            
            // Cerrar el modal después de procesar
            var registroModal = bootstrap.Modal.getInstance(document.getElementById('registro-modal'));
            registroModal.hide();
        });
    }

    // Manejar envío de formulario de contacto
    var contactoForm = document.getElementById('contacto-form');
    if (contactoForm) {
        contactoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!this.checkValidity()) {
                e.stopPropagation();
                this.classList.add('was-validated');
                return;
            }
            
            // Aquí iría la lógica para enviar los datos al servidor y generar el correo
            alert('Consulta enviada correctamente. Te responderemos a la mayor brevedad posible.');
            
            // Cerrar el modal después de procesar
            var contactoModal = bootstrap.Modal.getInstance(document.getElementById('contacto-modal'));
            contactoModal.hide();
        });
    }
});

// Función para inicializar FullCalendar
function initCalendar() {
    var calendarEl = document.getElementById('calendar');
    
    if (calendarEl) {
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,listMonth'
            },
            locale: 'es',
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                list: 'Lista'
            },
            firstDay: 1, // Lunes como primer día de la semana
            height: 'auto',
            events: [
                // Ejemplos de eventos predefinidos
                {
                    title: 'Retiro Mensual',
                    start: '2025-01-10',
                    classNames: ['evento-retiro']
                },
                {
                    title: 'Conferencia Familiar',
                    start: '2025-01-25',
                    classNames: ['evento-conferencia']
                },
                {
                    title: 'Retiro Mensual',
                    start: '2025-02-14',
                    classNames: ['evento-retiro']
                }
                // Los eventos reales se cargarán desde la base de datos
            ],
            eventClick: function(info) {
                // Al hacer clic en un evento del calendario, abrir su modal correspondiente
                // Aquí habría que identificar el evento y abrir su modal específico
                alert('Evento: ' + info.event.title);
            }
        });
        
        calendar.render();
    }
}

// Función para cargar eventos desde la API
function cargarEventos() {
    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => {
            // Procesar y mostrar los eventos
            mostrarEventos(data);
        })
        .catch(error => {
            console.error('Error al cargar eventos:', error);
        });
}

// Función para mostrar eventos
function mostrarEventos(eventos) {
    var eventosPorMes = {};
    
    // Agrupar eventos por mes
    eventos.forEach(evento => {
        var fecha = new Date(evento.fecha);
        var mes = fecha.toLocaleString('es', { month: 'long' }).toUpperCase();
        
        if (!eventosPorMes[mes]) {
            eventosPorMes[mes] = [];
        }
        
        eventosPorMes[mes].push(evento);
    });
    
    // Crear HTML para los eventos
    var eventosContainer = document.querySelector('.eventos-container');
    if (eventosContainer) {
        eventosContainer.innerHTML = '';
        
        for (var mes in eventosPorMes) {
            var mesEl = document.createElement('div');
            mesEl.className = 'evento-mes';
            
            var mesTitulo = document.createElement('h3');
            mesTitulo.className = 'mes-titulo';
            mesTitulo.textContent = mes;
            mesEl.appendChild(mesTitulo);
            
            eventosPorMes[mes].forEach(evento => {
                var eventoItem = document.createElement('div');
                eventoItem.className = 'evento-item';
                eventoItem.setAttribute('data-evento-id', evento.id);
                
                var fecha = new Date(evento.fecha);
                var diaSemana = fecha.toLocaleString('es', { weekday: 'long' });
                var diaNumero = fecha.getDate();
                
                eventoItem.innerHTML = `
                    <p>${diaSemana.charAt(0).toUpperCase() + diaSemana.slice(1)}, ${diaNumero} - ${evento.titulo}</p>
                `;
                
                eventoItem.addEventListener('click', function() {
                    abrirModalEvento(evento);
                });
                
                mesEl.appendChild(eventoItem);
            });
            
            eventosContainer.appendChild(mesEl);
        }
    }
}

// Función para abrir modal de evento específico
function abrirModalEvento(evento) {
    var modalTemplate = document.getElementById('evento-modal-template');
    var modal = new bootstrap.Modal(modalTemplate);
    
    // Configurar el contenido del modal con los datos del evento
    modalTemplate.querySelector('.modal-title').textContent = evento.titulo;
    modalTemplate.querySelector('.evento-fecha').textContent = formatoFecha(evento.fecha);
    modalTemplate.querySelector('.evento-lugar').textContent = evento.lugar;
    modalTemplate.querySelector('.evento-descripcion').textContent = evento.descripcion;
    modalTemplate.querySelector('.evento-precio').textContent = evento.precio + ' €';
    
    // Guardar el ID del evento para el formulario de inscripción
    modalTemplate.querySelector('.inscripcion-btn').setAttribute('data-evento-id', evento.id);
    
    modal.show();
}

// Función para formatear fecha
function formatoFecha(fechaStr) {
    var fecha = new Date(fechaStr);
    var opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return fecha.toLocaleDateString('es-ES', opciones);
}
