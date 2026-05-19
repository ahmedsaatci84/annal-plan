/**
 * Activity progress inline update
 * Sends PATCH to /plans/api/activities/<pk>/progress/ and updates the UI
 */
document.addEventListener('DOMContentLoaded', function () {

    // Handle activity progress form submissions via AJAX
    document.querySelectorAll('[data-progress-form]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const activityId = form.dataset.activityId;
            const formData = new FormData(form);
            const data = {};
            formData.forEach((v, k) => { data[k] = v; });

            fetch(`/plans/api/activities/${activityId}/progress/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': data.csrfmiddlewaretoken,
                },
                body: JSON.stringify({
                    actual_completion_pct: data.actual_completion_pct,
                    activity_status: data.activity_status,
                }),
            })
            .then(res => res.json())
            .then(result => {
                if (result.success) {
                    // Update progress bar
                    const row = document.querySelector(`[data-activity-row="${activityId}"]`);
                    if (row) {
                        const bar = row.querySelector('.actual-pct-bar');
                        if (bar) {
                            bar.style.width = result.actual_completion_pct + '%';
                            bar.textContent = result.actual_completion_pct + '%';
                        }
                        const statusBadge = row.querySelector('.activity-status-badge');
                        if (statusBadge) {
                            statusBadge.textContent = result.activity_status_display;
                        }
                    }
                    showToast('تم تحديث النشاط بنجاح', 'success');
                } else {
                    showToast(result.error || 'حدث خطأ أثناء التحديث', 'danger');
                }
            })
            .catch(() => showToast('تعذّر الاتصال بالخادم', 'danger'));
        });
    });

    function showToast(message, type) {
        const container = document.getElementById('toast-container') || createToastContainer();
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-bg-${type} border-0 show`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>`;
        container.appendChild(toastEl);
        setTimeout(() => toastEl.remove(), 4000);
    }

    function createToastContainer() {
        const div = document.createElement('div');
        div.id = 'toast-container';
        div.className = 'toast-container position-fixed bottom-0 start-0 p-3';
        div.style.zIndex = '9999';
        document.body.appendChild(div);
        return div;
    }
});
