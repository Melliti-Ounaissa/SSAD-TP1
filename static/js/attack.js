// static/js/attack.js

async function runAttack() {
    const cipherType = document.getElementById('cipher-type').value;
    const ciphertext = document.getElementById('ciphertext-input').value.trim();
    const resultsList = document.getElementById('results-list');
    const errorMessage = document.getElementById('attack-error-message');
    
    errorMessage.textContent = '';
    resultsList.innerHTML = '<p>Running attack...</p>';

    if (!ciphertext) {
        errorMessage.textContent = 'Please enter a ciphertext.';
        resultsList.innerHTML = '<p>Results will appear here...</p>';
        return;
    }

    try {
        const response = await fetch('/api/crypto/attack', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cipher_type: cipherType, ciphertext: ciphertext })
        });

        const data = await response.json();

        if (data.success) {
            resultsList.innerHTML = `<h4>${data.type} - Found ${data.results.length} results:</h4>`;
            
            if (data.results.length === 0) {
                resultsList.innerHTML += '<p>No results found with the current attack method/dictionary.</p>';
                return;
            }
            
            data.results.forEach(result => {
                const item = document.createElement('div');
                item.className = 'result-item';
                if (result.is_likely) {
                    item.classList.add('likely');
                }
                
                item.innerHTML = `
                    <strong>Key: <span>${result.key}</span></strong> 
                    <br> 
                    Plaintext: <span>${result.plaintext}</span>
                `;
                resultsList.appendChild(item);
            });
            
        } else {
            errorMessage.textContent = 'Attack Failed: ' + data.message;
            resultsList.innerHTML = '<p>Error during attack.</p>';
        }

    } catch (error) {
        console.error('Error running attack:', error);
        errorMessage.textContent = 'An unexpected error occurred during the attack.';
        resultsList.innerHTML = '<p>Error during attack.</p>';
    }
}