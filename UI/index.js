// --- UPDATED JavaScript Logic for the Analyzer ---
async function analyzeSentiment() {
    const textInput = document.getElementById('text-input');
    const analyzeButton = document.getElementById('analyze-button');
    const resultContainer = document.getElementById('result-container');
    const resultText = document.getElementById('result-text');
    const text = textInput.value;

    // The URL for your Flask backend's predict endpoint.
    const backendUrl = 'http://127.0.0.1:5000/predict';

    if (!text.trim()) {
        textInput.classList.add('border-red-500', 'ring-red-500');
        textInput.placeholder = "Please enter some text first!";
        setTimeout(() => {
            textInput.classList.remove('border-red-500', 'ring-red-500');
            textInput.placeholder = "e.g., 'The customer service was incredibly helpful and friendly!'";
        }, 3000);
        return;
    }

    // Disable button and show loading state
    analyzeButton.disabled = true;
    analyzeButton.textContent = 'Analyzing...';

    try {
        // --- Real API Call to the Backend ---
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            // Handle HTTP errors (e.g., 400, 500)
            const errorData = await response.json();
            throw new Error(errorData.error || `Server responded with status: ${response.status}`);
        }

        const data = await response.json();

        // Display the result with the sentiment and confidence score
        const confidence = (data.score * 100).toFixed(1);
        resultText.textContent = `Sentiment: ${data.sentiment} (Confidence: ${confidence}%)`;

        // Update UI colors based on the result
        resultContainer.classList.remove('hidden', 'POSITIVE', 'NEGATIVE');
        resultContainer.classList.add(data.sentiment); // Class names are POSITIVE/NEGATIVE

    } catch (error) {
        // Handle network errors or errors from the backend
        resultText.textContent = `Error: ${error.message}`;
        resultContainer.classList.remove('hidden', 'POSITIVE');
        resultContainer.classList.add('NEGATIVE');
        console.error("Analysis Error:", error);
    } finally {
        // Re-enable the button regardless of success or failure
        analyzeButton.disabled = false;
        analyzeButton.textContent = 'Analyze Sentiment';
    }
}