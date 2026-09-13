const passwordInput = document.getElementById('passwordInput');
const toggleBtn = document.getElementById('toggleVisibility');
const strengthBar = document.getElementById('strengthBar');
const strengthLabel = document.getElementById('strengthLabel');
const strengthScore = document.getElementById('strengthScore');
const resultsSection = document.getElementById('results');
const generateBtn = document.getElementById('generatePassword');

let debounceTimer;

if (passwordInput) {
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        if (password.length === 0) { resetUI(); return; }
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => analyzePassword(password), 300);
    });
}

if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
        toggleBtn.textContent = passwordInput.type === 'password' ? '👁️' : '🙈';
    });
}

if (generateBtn) {
    generateBtn.addEventListener('click', generatePassword);
}

async function analyzePassword(password) {
    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        if (!res.ok) throw new Error('Analysis failed');
        const data = await res.json();
        updateUI(data);
    } catch (err) { console.error(err); }
}

function updateUI(data) {
    const score = data.score || 0;
    const strength = data.strength || 'weak';

    strengthBar.style.width = `${score}%`;
    strengthBar.style.background = getStrengthColor(strength);
    strengthLabel.textContent = strength.charAt(0).toUpperCase() + strength.slice(1);
    strengthLabel.className = `strength-label ${strength}`;
    strengthScore.textContent = `${score}/100`;

    resultsSection.classList.remove('hidden');
    updateMetrics(data.metrics);
    updateFeedback(data.feedback);
    updateAdvancedMetrics(data);
    updateHash(data.hash);
}

function updateMetrics(m) {
    if (!m) return;
    const labels = {
        length: 'Length',
        lowercase_count: 'Lowercase',
        uppercase_count: 'Uppercase',
        digit_count: 'Digits',
        special_count: 'Special',
        unique_characters: 'Unique'
    };
    let html = '';
    for (const [k, label] of Object.entries(labels)) {
        if (m[k] !== undefined) {
            html += `<div class="metric-item"><span class="metric-label">${label}</span><span class="metric-value">${m[k]}</span></div>`;
        }
    }
    document.getElementById('metricsContainer').innerHTML = html;
}

function updateFeedback(fb) {
    const list = document.getElementById('feedbackList');
    if (!fb || fb.length === 0) {
        list.innerHTML = '<li>✅ No issues found! Great password!</li>';
        return;
    }
    list.innerHTML = fb.map(item => `<li>${item}</li>`).join('');
}

function updateAdvancedMetrics(data) {
    const m = data.metrics || {};
    const metrics = [
        { label: 'Entropy', value: `${data.entropy || 0} bits` },
        { label: 'Char Set', value: `${m.character_set_size || 0}` },
        { label: 'Uppercase', value: m.has_uppercase ? '✅' : '❌' },
        { label: 'Lowercase', value: m.has_lowercase ? '✅' : '❌' },
        { label: 'Numbers', value: m.has_digits ? '✅' : '❌' },
        { label: 'Special', value: m.has_special ? '✅' : '❌' }
    ];

    if (data.ml_prediction && !data.ml_prediction.error) {
        metrics.push({ label: '🤖 ML Prediction', value: data.ml_prediction.label.toUpperCase() });
        metrics.push({ label: '🎯 ML Confidence', value: `${data.ml_prediction.confidence}%` });
    }

    document.getElementById('advancedMetrics').innerHTML = metrics.map(x =>
        `<div class="advanced-metric"><span class="metric-label">${x.label}</span><span class="metric-value">${x.value}</span></div>`
    ).join('');
}

function updateHash(h) {
    const c = document.getElementById('hashContainer');
    if (!h) { c.innerHTML = '<p class="hash-info">Hash will be displayed here</p>'; return; }
    c.innerHTML = `
        <p class="hash-info">🔒 Hashed using ${h.algorithm}</p>
        <div style="font-size:0.75rem;color:#a0aec0;margin-bottom:8px;">Salt: ${h.salt.substring(0, 16)}...</div>
        <div>${h.hash}</div>`;
}

async function generatePassword() {
    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length: 20 })
        });
        const data = await res.json();
        passwordInput.value = data.password;
        passwordInput.type = 'text';
        analyzePassword(data.password);
    } catch (e) { console.error(e); }
}

function resetUI() {
    strengthBar.style.width = '0%';
    strengthLabel.textContent = 'Weak';
    strengthLabel.className = 'strength-label weak';
    strengthScore.textContent = '0/100';
    resultsSection.classList.add('hidden');
}

function getStrengthColor(s) {
    return { weak: '#fc8181', medium: '#f6ad55', strong: '#68d391' }[s] || '#e2e8f0';
}

console.log('✅ script.js loaded successfully');