// theme-manager.js
import { showToast } from '../utils/common-utils.js';

export class ThemeManager {
    constructor() {
        this.themeToggleBtn = document.getElementById('themeToggle');
        this.iconEl = document.getElementById('themeIcon');
        this.textEl = document.querySelector('.theme-text');
        this.init();
    }
    init() {
        const saved = localStorage.getItem('theme') || 'light';
        this.applyTheme(saved);
        if (this.themeToggleBtn) {
            this.themeToggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    }
    applyTheme(name) {
        if (name === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (this.iconEl) this.iconEl.textContent = '☀️';
            if (this.themeToggleBtn) this.themeToggleBtn.title = '切换到日间主题';
            if (this.textEl) this.textEl.textContent = '日间模式';
        } else {
            document.documentElement.removeAttribute('data-theme');
            if (this.iconEl) this.iconEl.textContent = '🌙';
            if (this.themeToggleBtn) this.themeToggleBtn.title = '切换到夜间主题';
            if (this.textEl) this.textEl.textContent = '夜间模式';
        }
        localStorage.setItem('theme', name);
    }
    toggleTheme() {
        const current = localStorage.getItem('theme') || 'light';
        const next = current === 'light' ? 'dark' : 'light';
        this.applyTheme(next);
        showToast(next === 'dark' ? '已切换到夜间模式' : '已切换到日间模式');
    }
}
