/**
 * Gantt chart renderer using Chart.js bar chart (horizontal)
 * Data is fetched from /plans/api/<planId>/gantt-data/
 */
(function () {
    const container = document.getElementById('gantt-canvas-container');
    if (!container) return;

    const planId = container.dataset.planId;
    if (!planId) return;

    fetch(`/plans/api/${planId}/gantt-data/`)
        .then(r => r.json())
        .then(data => renderGantt(data, container))
        .catch(err => {
            container.innerHTML = '<div class="alert alert-warning">تعذّر تحميل بيانات Gantt</div>';
            console.error(err);
        });

    const STATUS_COLORS = {
        'NOT_STARTED': '#adb5bd',
        'IN_PROGRESS':  '#ffc107',
        'COMPLETED':    '#198754',
        'DELAYED':      '#dc3545',
        'ROLLED_OVER':  '#fd7e14',
        'STOPPED':      '#6c757d',
    };

    function renderGantt(data, container) {
        if (!data.rows || data.rows.length === 0) {
            container.innerHTML = '<div class="alert alert-info">لا يوجد أنشطة لعرضها في الجدول الزمني.</div>';
            return;
        }

        const months = data.months.map(m => m.name);
        const labels = data.rows.map(r => `${r.activity_code} — ${r.title.substring(0, 30)}`);

        // Build dataset per row (each row is a single horizontal bar spanning its active months)
        const datasets = data.rows.map((row, idx) => {
            const startIdx = row.months_active.indexOf(true);
            const endIdx   = row.months_active.lastIndexOf(true);
            if (startIdx < 0) return null;

            return {
                label: row.title,
                data: labels.map((_, i) => i === idx ? [startIdx, endIdx + 1] : null),
                backgroundColor: STATUS_COLORS[row.status] || '#0d6efd',
                borderColor: 'rgba(0,0,0,0.1)',
                borderWidth: 1,
                borderRadius: 3,
            };
        }).filter(Boolean);

        const canvas = document.createElement('canvas');
        canvas.style.width = '100%';
        canvas.style.height = Math.max(300, data.rows.length * 28) + 'px';
        container.innerHTML = '';
        container.appendChild(canvas);

        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels, datasets },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (items) => labels[items[0].dataIndex],
                            label: (item) => {
                                const [s, e] = item.raw;
                                return `${months[s]} — ${months[e - 1]}`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        min: 0,
                        max: 12,
                        ticks: {
                            callback: (v) => months[v] || '',
                            stepSize: 1,
                        },
                        grid: { color: '#dee2e6' },
                    },
                    y: {
                        ticks: { font: { size: 11 } },
                    },
                },
            },
        });
    }
})();
