// Simple search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) return;
    
    let searchIndex = [];
    
    // Load search index
    fetch('/index.json')
        .then(response => response.json())
        .then(data => {
            searchIndex = data;
        })
        .catch(error => console.error('Error loading search index:', error));
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }
        
        const results = searchIndex.filter(item => 
            item.title.toLowerCase().includes(query) ||
            item.content.toLowerCase().includes(query) ||
            (item.tags && item.tags.some(tag => tag.toLowerCase().includes(query)))
        );
        
        displayResults(results);
    });
    
    function displayResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = '<p>No results found.</p>';
            return;
        }
        
        const html = results.map(result => `
            <div class="search-result">
                <h3><a href="${result.permalink}">${result.title}</a></h3>
                <p>${result.summary}</p>
                <div class="search-meta">
                    <time>${new Date(result.date).toLocaleDateString()}</time>
                    ${result.tags ? `<span class="tags">${result.tags.map(tag => `<a href="/tags/${tag.toLowerCase()}">${tag}</a>`).join(', ')}</span>` : ''}
                </div>
            </div>
        `).join('');
        
        searchResults.innerHTML = html;
    }
});

