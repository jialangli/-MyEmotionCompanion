// persona-manager.js
import { CONFIG } from '../config/constants.js';

export class PersonaManager {
    constructor() {
        this.selectEl = document.getElementById('personaSelect');
        this.currentPersonaId = localStorage.getItem('selectedPersona') || 'warm_partner';
    }
    async loadPersonas() {
        try {
            const res = await fetch(CONFIG.apiUrl.replace('/chat', '/personas'));
            const data = await res.json();
            if (data.status === 'success') {
                this.renderPersonas(data.personas);
            }
        } catch (e) {
            this.renderPersonas([
                { id: 'warm_partner', name: '暖心伴侣（女友）', emoji: '💕' }
            ]);
        }
    }
    renderPersonas(personas) {
        this.selectEl.innerHTML = '';
        personas.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `${p.emoji || ''} ${p.name}`;
            if (p.id === this.currentPersonaId) opt.selected = true;
            this.selectEl.appendChild(opt);
        });
        this.selectEl.addEventListener('change', () => {
            this.currentPersonaId = this.selectEl.value;
            localStorage.setItem('selectedPersona', this.currentPersonaId);
        });
    }
    getCurrentPersonaId() {
        return this.currentPersonaId;
    }
}
