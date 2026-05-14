// Carregar medicamentos ao abrir o dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadMedications();
});

async function loadMedications() {
    try {
        const response = await fetch('/api/medications');
        
        if (!response.ok) {
            throw new Error('Erro ao carregar medicamentos');
        }
        
        const medications = await response.json();
        const container = document.getElementById('medications-list');
        
        if (medications.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <h3>Nenhum medicamento cadastrado</h3>
                    <p>Comece cadastrando seu primeiro medicamento.</p>
                    <a href="/register" class="btn-primary">+ Novo Medicamento</a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = medications.map(med => createMedicationCard(med)).join('');
        
        // Adicionar listeners aos botões de ação
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const medId = e.target.dataset.medId;
                deleteMedication(medId);
            });
        });
        
    } catch (error) {
        console.error('Erro:', error);
        document.getElementById('medications-list').innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <h3>⚠️ Erro</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function createMedicationCard(medication) {
    const nextIntake = medication.next_intake 
        ? new Date(medication.next_intake).toLocaleString('pt-BR')
        : 'Não agendado';
    
    const lastIntake = medication.last_intake 
        ? new Date(medication.last_intake).toLocaleString('pt-BR')
        : 'Nunca ingerido';
    
    // Determinar status
    let statusClass = 'status-next';
    let statusText = 'Próximo agendado';
    
    if (medication.last_intake) {
        statusClass = 'status-confirmed';
        statusText = 'Última ingestão confirmada';
    }
    
    return `
        <div class="medication-card">
            <h3>💊 ${escapeHtml(medication.name)}</h3>
            
            <div class="medication-time">
                🕐 ${medication.time}
            </div>
            
            <div class="medication-info">
                <label>Dosagem:</label>
                <span>${escapeHtml(medication.dosage)}</span>
            </div>
            
            <div class="medication-info">
                <label>Intervalo:</label>
                <span>${medication.interval_hours}h</span>
            </div>
            
            <div class="medication-info">
                <label>E-mail:</label>
                <span>${escapeHtml(medication.email)}</span>
            </div>
            
            <div class="medication-info">
                <label>Última ingestão:</label>
                <span>${lastIntake}</span>
            </div>
            
            <div class="medication-info">
                <label>Próximo:</label>
                <span>${nextIntake}</span>
            </div>
            
            <span class="status-badge ${statusClass}">${statusText}</span>
            
            <div class="medication-actions">
                <button class="btn-small btn-delete" data-med-id="${medication.id}">
                    🗑️ Remover
                </button>
            </div>
        </div>
    `;
}

async function deleteMedication(medId) {
    if (!confirm('Tem certeza que deseja remover este medicamento?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/medications/${medId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erro ao remover medicamento');
        }
        
        alert('Medicamento removido com sucesso!');
        loadMedications();
        
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao remover medicamento: ' + error.message);
    }
}

// Função auxiliar para escapar HTML e prevenir XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Auto-reload a cada 30 segundos para atualizar status
setInterval(() => {
    loadMedications();
}, 30000);
