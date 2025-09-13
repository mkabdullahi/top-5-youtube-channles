// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Platform connection status updates
    setupPlatformConnections();

    // Real-time metric updates
    setupMetricUpdates();

    // Infinite scroll for influencer lists
    setupInfiniteScroll();
});

function setupPlatformConnections() {
    document.querySelectorAll('.platform-connect').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const platform = this.dataset.platform;
            
            try {
                const response = await fetch(`/auth/oauth/connect/${platform}`);
                if (response.ok) {
                    window.location.href = await response.text();
                } else {
                    showError('Failed to connect to platform');
                }
            } catch (error) {
                showError('Connection error');
                console.error('Error:', error);
            }
        });
    });
}

function setupMetricUpdates() {
    if (document.querySelector('.metrics-container')) {
        setInterval(async function() {
            const containers = document.querySelectorAll('.metrics-container');
            
            for (const container of containers) {
                const platform = container.dataset.platform;
                const influencerId = container.dataset.influencerId;
                
                try {
                    const response = await fetch(`/api/metrics/${platform}/${influencerId}`);
                    if (response.ok) {
                        const metrics = await response.json();
                        updateMetricsDisplay(container, metrics);
                    }
                } catch (error) {
                    console.error('Metrics update error:', error);
                }
            }
        }, 60000); // Update every minute
    }
}

function updateMetricsDisplay(container, metrics) {
    Object.entries(metrics).forEach(([key, value]) => {
        const element = container.querySelector(`.metric-${key}`);
        if (element) {
            element.textContent = formatNumber(value);
            element.classList.add('updated');
            setTimeout(() => element.classList.remove('updated'), 1000);
        }
    });
}

function setupInfiniteScroll() {
    const influencersList = document.querySelector('.influencers-list');
    if (influencersList) {
        let page = 1;
        let loading = false;
        
        window.addEventListener('scroll', async function() {
            if (loading) return;
            
            const {scrollTop, scrollHeight, clientHeight} = document.documentElement;
            
            if (scrollTop + clientHeight >= scrollHeight - 5) {
                loading = true;
                
                try {
                    const category = influencersList.dataset.category;
                    const platform = document.querySelector('.platform-filter.active').dataset.platform;
                    
                    const response = await fetch(`/api/influencers/top/${category}?platform=${platform}&page=${++page}`);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.length > 0) {
                            appendInfluencers(data);
                        }
                    }
                } catch (error) {
                    console.error('Load more error:', error);
                } finally {
                    loading = false;
                }
            }
        });
    }
}

function appendInfluencers(influencers) {
    const container = document.querySelector('.influencers-list');
    
    influencers.forEach(influencer => {
        const card = createInfluencerCard(influencer);
        container.appendChild(card);
    });
}

function createInfluencerCard(influencer) {
    const div = document.createElement('div');
    div.className = 'col-md-4 mb-3';
    div.innerHTML = `
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">${influencer.name}</h5>
                <p class="card-text">
                    <small class="text-muted">Platform: ${influencer.platform}</small>
                </p>
                <div class="metrics-container" data-platform="${influencer.platform}" data-influencer-id="${influencer.id}">
                    ${renderMetrics(influencer.metrics)}
                </div>
            </div>
        </div>
    `;
    return div;
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num;
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('main').prepend(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}