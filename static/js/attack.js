// Tab switching functionality
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tab = button.dataset.tab;
        
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        button.classList.add('active');
        document.getElementById(tab).classList.add('active');
    });
});

// Brute Force Attack
document.getElementById('start-brute-force').addEventListener('click', async () => {
    const ciphertext = document.getElementById('bf-ciphertext').value.trim();
    const algorithm = document.getElementById('bf-algorithm').value;
    
    if (!ciphertext) {
        alert('Please enter a ciphertext to attack');
        return;
    }

    const resultsSection = document.getElementById('bf-results');
    const resultsList = document.getElementById('bf-results-list');
    const button = document.getElementById('start-brute-force');
    
    resultsSection.classList.add('show');
    resultsList.innerHTML = '<p style="text-align: center; color: #666;">Running attack...</p>';
    button.disabled = true;
    button.textContent = '⏳ Attacking...';
    
    // Reset stats
    document.getElementById('bf-tested').textContent = '0';
    document.getElementById('bf-found').textContent = '0';
    document.getElementById('bf-time').textContent = '0s';
    document.getElementById('bf-progress').style.width = '0%';
    document.getElementById('bf-progress').textContent = '0%';
    
    const startTime = Date.now();
    
    try {
        const response = await fetch('/api/crypto/attack', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                cipher_type: algorithm,
                ciphertext: ciphertext
            })
        });

        const data = await response.json();
        
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('bf-time').textContent = elapsed + 's';

        if (data.success && data.results) {
            displayResults('bf', data.results, data.type);
        } else {
            resultsList.innerHTML = `<p style="text-align: center; color: #dc3545;">Attack failed: ${data.message || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error:', error);
        resultsList.innerHTML = '<p style="text-align: center; color: #dc3545;">Error during attack. Please try again.</p>';
    } finally {
        button.disabled = false;
        button.textContent = '🚀 Start Brute Force Attack';
    }
});

// Dictionary Attack
document.getElementById('start-dictionary').addEventListener('click', async () => {
    const ciphertext = document.getElementById('dict-ciphertext').value.trim();
    const algorithm = document.getElementById('dict-algorithm').value;
    
    if (!ciphertext) {
        alert('Please enter a ciphertext to attack');
        return;
    }

    const resultsSection = document.getElementById('dict-results');
    const resultsList = document.getElementById('dict-results-list');
    const button = document.getElementById('start-dictionary');
    
    resultsSection.classList.add('show');
    resultsList.innerHTML = '<p style="text-align: center; color: #666;">Running attack...</p>';
    button.disabled = true;
    button.textContent = '⏳ Attacking...';
    
    // Reset stats
    document.getElementById('dict-tested').textContent = '0';
    document.getElementById('dict-found').textContent = '0';
    document.getElementById('dict-time').textContent = '0s';
    document.getElementById('dict-progress').style.width = '0%';
    document.getElementById('dict-progress').textContent = '0%';
    
    const startTime = Date.now();
    
    try {
        const response = await fetch('/api/crypto/attack', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                cipher_type: algorithm,
                ciphertext: ciphertext
            })
        });

        const data = await response.json();
        
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('dict-time').textContent = elapsed + 's';

        if (data.success && data.results) {
            displayResults('dict', data.results, data.type);
        } else {
            resultsList.innerHTML = `<p style="text-align: center; color: #dc3545;">Attack failed: ${data.message || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error:', error);
        resultsList.innerHTML = '<p style="text-align: center; color: #dc3545;">Error during attack. Please try again.</p>';
    } finally {
        button.disabled = false;
        button.textContent = '🚀 Start Dictionary Attack';
    }
});

// Display results function
function displayResults(type, results, attackType) {
    const resultsList = document.getElementById(`${type}-results-list`);
    const tested = results.length;
    const found = results.filter(r => r.is_likely).length;
    
    document.getElementById(`${type}-tested`).textContent = tested.toLocaleString();
    document.getElementById(`${type}-found`).textContent = found;
    document.getElementById(`${type}-progress`).style.width = '100%';
    document.getElementById(`${type}-progress`).textContent = '100%';
    
    if (results.length === 0) {
        resultsList.innerHTML = '<p style="text-align: center; color: #999;">No results found with the current attack method.</p>';
        return;
    }
    
    resultsList.innerHTML = `<div style="margin-bottom: 15px; padding: 10px; background: #e8f4f8; border-radius: 5px; color: #0c5460;">
        <strong>${attackType}</strong> - Found ${results.length} result(s)
    </div>`;
    
    results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'result-item';
        if (result.is_likely) {
            item.classList.add('likely');
        }
        
        const icon = result.is_likely ? '✅' : '❌';
        
        item.innerHTML = `
            <div class="result-key">${icon} Key: ${escapeHtml(String(result.key))}</div>
            <div class="result-plaintext">Plaintext: ${escapeHtml(result.plaintext)}</div>
        `;
        
        resultsList.appendChild(item);
    });
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}