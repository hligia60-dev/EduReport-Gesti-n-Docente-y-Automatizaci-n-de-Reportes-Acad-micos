/**
 * EduReport - Lógica Interactiva del Cliente
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('EduReport inicializado correctamente.');

    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Simulador Interactivo de la Regla de 3 Ausencias
    let absenceCount = 0;
    const maxAbsences = 3;
    
    const countDisplay = document.getElementById('simAbsenceCount');
    const statusText = document.getElementById('simStatusText');
    const alertBox = document.getElementById('simSimulatorBox');
    const alertBadge = document.getElementById('simAlertBadge');
    const btnAdd = document.getElementById('simBtnAddAbsence');
    const btnReset = document.getElementById('simBtnReset');
    const btnGenerateReport = document.getElementById('simBtnGenerateReport');
    const dot1 = document.getElementById('simDot1');
    const dot2 = document.getElementById('simDot2');
    const dot3 = document.getElementById('simDot3');

    if (btnAdd && countDisplay) {
        btnAdd.addEventListener('click', function () {
            if (absenceCount < maxAbsences) {
                absenceCount++;
                updateSimulatorUI();
            }
        });

        btnReset.addEventListener('click', function () {
            absenceCount = 0;
            updateSimulatorUI();
        });

        if (btnGenerateReport) {
            btnGenerateReport.addEventListener('click', function () {
                const reportModal = new bootstrap.Modal(document.getElementById('reportPreviewModal'));
                reportModal.show();
            });
        }
    }

    function updateSimulatorUI() {
        if (!countDisplay) return;

        countDisplay.textContent = absenceCount;

        // Actualizar dots
        if (dot1) dot1.classList.toggle('active', absenceCount >= 1);
        if (dot2) dot2.classList.toggle('active', absenceCount >= 2);
        if (dot3) dot3.classList.toggle('active', absenceCount >= 3);

        // Regla específica: Alerta a las 3 ausencias
        if (absenceCount >= 3) {
            alertBox.classList.add('alert-active');
            alertBadge.classList.remove('d-none');
            alertBadge.classList.add('badge-pulse');
            statusText.innerHTML = '<span class="text-danger fw-bold"><i class="bi bi-exclamation-triangle-fill me-1"></i> ¡Alerta Crítica! Estudiante alcanzó el límite de 3 ausencias.</span>';
            btnAdd.disabled = true;
            btnGenerateReport.classList.remove('disabled');
            btnGenerateReport.removeAttribute('disabled');
        } else {
            alertBox.classList.remove('alert-active');
            alertBadge.classList.add('d-none');
            alertBadge.classList.remove('badge-pulse');
            btnAdd.disabled = false;
            btnGenerateReport.classList.add('disabled');
            btnGenerateReport.setAttribute('disabled', 'disabled');

            if (absenceCount === 0) {
                statusText.innerHTML = '<span class="text-success fw-medium"><i class="bi bi-check-circle-fill me-1"></i> Asistencia normal (0 ausencias).</span>';
            } else if (absenceCount === 1) {
                statusText.innerHTML = '<span class="text-secondary fw-medium"><i class="bi bi-info-circle me-1"></i> 1 ausencia registrada. Sin alerta.</span>';
            } else if (absenceCount === 2) {
                statusText.innerHTML = '<span class="text-warning fw-bold"><i class="bi bi-exclamation-circle me-1"></i> 2 ausencias registradas. ¡Atención preventiva!</span>';
            }
        }
    }
});
