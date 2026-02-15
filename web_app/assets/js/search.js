// Search Bhagavad Gita verses from cleaned dataset
// Use relative path from web_app folder to data folder

const DATASET_URL = '../data/cleaned/gita_master.json';

async function fetchGitaData() {
    console.log('Fetching Gita data from:', DATASET_URL);
    const response = await fetch(DATASET_URL);
    if (!response.ok) {
        console.error('Fetch failed with status:', response.status);
        throw new Error('Failed to load Gita dataset');
    }
    return await response.json();
}

function searchVerses(query, gitaData) {
    const results = [];
    const q = query.trim().toLowerCase();
    gitaData.chapters.forEach(chapter => {
        chapter.verses.forEach(verse => {
            // Search in English, Hindi, Sanskrit, transliteration
            const fields = [verse.english, verse.hindi, verse.sanskrit, verse.transliteration];
            if (fields.some(text => text && text.toLowerCase().includes(q))) {
                results.push({
                    chapter_number: chapter.chapter_number,
                    chapter_name: chapter.chapter_name.english,
                    verse_number: verse.verse_number,
                    english: verse.english,
                    hindi: verse.hindi,
                    sanskrit: verse.sanskrit,
                    transliteration: verse.transliteration
                });
            }
        });
    });
    return results;
}

// UI integration
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsDiv = document.getElementById('search-results');

    let gitaData = null;

    // Load dataset
    fetchGitaData()
        .then(data => {
            gitaData = data;
            console.log('Gita dataset loaded successfully!', data.metadata);
            resultsDiv.innerHTML = '<p style="color:green;">Type your Keyword to search like Arjuna, Krishna, pandava.</p>';
        })
        .catch(err => {
            console.error('Failed to load Gita dataset:', err);
            resultsDiv.innerHTML = '<p style="color:red;">Error loading Bhagavad Gita data. Check console for details.</p>';
        });

    function performSearch() {
        if (!gitaData) {
            resultsDiv.innerHTML = '<p>Loading data... Please wait.</p>';
            return;
        }
        const query = searchInput.value.trim();
        if (!query) {
            resultsDiv.innerHTML = '<p>Please enter a search term.</p>';
            return;
        }
        const results = searchVerses(query, gitaData);
        console.log(`Search for "${query}" returned ${results.length} results`);
        if (results.length === 0) {
            resultsDiv.innerHTML = '<p>No verses found.</p>';
        } else {
            resultsDiv.innerHTML = results.map(r =>
                `<div class="verse-result">
                    <b>Chapter ${r.chapter_number}: ${r.chapter_name}</b><br>
                    <b>Verse ${r.verse_number}</b><br>
                    <span><b>Sanskrit:</b> ${r.sanskrit}</span><br>
                    <span><b>Transliteration:</b> ${r.transliteration}</span><br>
                    <span><b>English:</b> ${r.english}</span><br>
                    <span><b>Hindi:</b> ${r.hindi}</span>
                </div>`
            ).join('');
        }
    }

    // Click and Enter key support
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
});
