document.addEventListener('DOMContentLoaded', function () {

    // ═══════════════════════════
    // STATE
    // ═══════════════════════════
    let currentStep        = 0;
    let moduleFilesStore   = [];
    let occupiedTimesStore = [];
    let studyAppsStore     = [];

    // ═══════════════════════════
    // ELEMENT REFS
    // ═══════════════════════════
    const generateBtn     = document.getElementById('generateBtn');
    const progressFill    = document.getElementById('wizardProgressFill');

    const classInput      = document.getElementById('class_timetable');
    const moduleInput     = document.getElementById('module_timetables');
    const classFileList   = document.getElementById('classFileList');
    const modulePreviewBody  = document.getElementById('modulePreviewBody');
    const modulePreviewGroup = document.getElementById('modulePreviewGroup');
    const hiddenModuleFields = document.getElementById('hiddenModuleFields');

    const semesterStartDate  = document.getElementById('semester_start_date');
    const semesterEndDate    = document.getElementById('semester_end_date');
    const preferredStudyTime = document.getElementById('preferred_study_time');
    const sessionLength      = document.getElementById('session_length');

    const otTitle         = document.getElementById('ot_title');
    const otCategory      = document.getElementById('ot_category');
    const otDay           = document.getElementById('ot_day');
    const otStart         = document.getElementById('ot_start');
    const otEnd           = document.getElementById('ot_end');
    const otNotes         = document.getElementById('ot_notes');
    const occupiedList    = document.getElementById('occupiedList');
    const occupiedEmptyState = document.getElementById('occupiedEmptyState');
    const hiddenOccupiedFields = document.getElementById('hiddenOccupiedFields');

    const studyAppName       = document.getElementById('study_app_name');
    const studyAppType       = document.getElementById('study_app_type');
    const studyAppIdentifier = document.getElementById('study_app_identifier');
    const studyAppPurpose    = document.getElementById('study_app_purpose');
    const selectedAppsTray   = document.getElementById('selectedAppsTray');
    const trayPlaceholder    = document.getElementById('trayPlaceholder');
    const appCountBadge      = document.getElementById('appCountBadge');
    const hiddenStudyAppFields = document.getElementById('hiddenStudyAppFields');

    // ═══════════════════════════
    // HELPERS
    // ═══════════════════════════
    function esc(str) {
        return String(str ?? '')
            .replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
    function norm(id) { return String(id ?? '').trim().toLowerCase(); }
    function typeLabel(t) { return {desktop:'Desktop App',website:'Website',both:'Both'}[t] ?? t; }
    function fmtTime(t) {
        if (!t) return '—';
        const [h,m] = t.split(':');
        const hr = parseInt(h);
        return `${hr%12||12}:${m} ${hr>=12?'PM':'AM'}`;
    }
    function showErr(id, msg) { const e=document.getElementById(id); if(e) e.textContent=msg; }
    function clrErr(id)       { const e=document.getElementById(id); if(e) e.textContent=''; }
    function highlightBorder(el, bad) {
        el.style.borderColor = bad ? '#dc2626' : '';
        el.style.boxShadow   = bad ? '0 0 0 3px rgba(220,38,38,0.12)' : '';
    }

    // ═══════════════════════════
    // WIZARD NAVIGATION
    // ═══════════════════════════
    function goTo(n, skipValidation) {
        if (!skipValidation && n > currentStep) {
            if (!validateStep(currentStep)) return;
        }
        const panels = document.querySelectorAll('.wz-panel');
        const steps  = document.querySelectorAll('.wz-step');

        panels.forEach((p,i) => p.classList.toggle('active', i === n));

        steps.forEach((s,i) => {
            s.classList.remove('active','completed');
            if (i < n)       s.classList.add('completed');
            else if (i === n) s.classList.add('active');
        });

        // colour connectors
        for (let i = 0; i < 4; i++) {
            const c = document.getElementById('conn-'+i+'-'+(i+1));
            if (c) c.classList.toggle('completed', i < n);
        }

        progressFill.style.width = (n / 4 * 100) + '%';
        if (n === 4) buildReview();
        currentStep = n;

        // Scroll to top of form
        document.getElementById('studyPlanForm')
            .scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Wire up explicit nav buttons
    document.getElementById('next0').addEventListener('click', () => goTo(1));
    document.getElementById('back1').addEventListener('click', () => goTo(0, true));
    document.getElementById('next1').addEventListener('click', () => goTo(2));
    document.getElementById('back2').addEventListener('click', () => goTo(1, true));
    document.getElementById('next2').addEventListener('click', () => goTo(3));
    document.getElementById('back3').addEventListener('click', () => goTo(2, true));
    document.getElementById('next3').addEventListener('click', () => goTo(4));
    document.getElementById('back4').addEventListener('click', () => goTo(3, true));

    // Review edit buttons
    document.getElementById('editFiles').addEventListener('click',       () => goTo(0, true));
    document.getElementById('editStyle').addEventListener('click',       () => goTo(1, true));
    document.getElementById('editCommitments').addEventListener('click', () => goTo(2, true));
    document.getElementById('editApps').addEventListener('click',        () => goTo(3, true));

    // Clicking a completed step bubble jumps back
    document.querySelectorAll('.wz-step').forEach(s => {
        s.addEventListener('click', () => {
            const t = Number(s.dataset.step);
            if (t < currentStep) goTo(t, true);
        });
    });

    // ═══════════════════════════
    // STEP VALIDATION
    // ═══════════════════════════
    function validateStep(step) {
        if (step === 0) return validateStep0();
        if (step === 1) return validateStep1();
        return true;
    }

    function validateStep0() {
        let ok = true;
        if (!classInput.files.length) {
            showErr('classFileError', 'Please upload your class timetable.'); ok = false;
        } else clrErr('classFileError');

        if (!moduleFilesStore.length) {
            showErr('moduleFileError', 'Please upload at least one module timetable.'); ok = false;
        } else clrErr('moduleFileError');

        if (!semesterStartDate.value) {
            highlightBorder(semesterStartDate, true); ok = false;
        } else highlightBorder(semesterStartDate, false);

        if (!semesterEndDate.value) {
            highlightBorder(semesterEndDate, true); ok = false;
        } else if (semesterStartDate.value && semesterEndDate.value <= semesterStartDate.value) {
            highlightBorder(semesterEndDate, true);
            showErr('classFileError', 'End date must be after start date.'); ok = false;
        } else highlightBorder(semesterEndDate, false);

        return ok;
    }

    function validateStep1() {
        let ok = true;
        if (!document.querySelector('input[name="study_intensity"]:checked')) {
            showErr('intensityError', 'Please select a study intensity.'); ok = false;
        } else clrErr('intensityError');

        if (!preferredStudyTime.value) {
            highlightBorder(preferredStudyTime, true); ok = false;
        } else highlightBorder(preferredStudyTime, false);

        if (!sessionLength.value) {
            highlightBorder(sessionLength, true); ok = false;
        } else highlightBorder(sessionLength, false);

        if (!document.querySelector('input[name="break_preference"]:checked')) {
            showErr('breakError', 'Please select a break preference.'); ok = false;
        } else clrErr('breakError');

        return ok;
    }

    function validateFinalForm() {
        const ok =
            classInput.files.length > 0 &&
            moduleFilesStore.length > 0 &&
            !!semesterStartDate.value &&
            !!semesterEndDate.value &&
            !!document.querySelector('input[name="study_intensity"]:checked') &&
            !!preferredStudyTime.value &&
            !!sessionLength.value &&
            !!document.querySelector('input[name="break_preference"]:checked') &&
            studyAppsStore.length > 0;
        generateBtn.disabled = !ok;
    }

    // ═══════════════════════════
    // DRAG & DROP
    // ═══════════════════════════
    function setupDragDrop(zoneId, input) {
        const zone = document.getElementById(zoneId);
        zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
        zone.addEventListener('drop', e => {
            e.preventDefault(); zone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                const dt = new DataTransfer();
                Array.from(e.dataTransfer.files).forEach(f => dt.items.add(f));
                input.files = dt.files;
                input.dispatchEvent(new Event('change'));
            }
        });
    }
    setupDragDrop('classDropZone',  classInput);
    setupDragDrop('moduleDropZone', moduleInput);

    // ═══════════════════════════
    // CLASS TIMETABLE
    // ═══════════════════════════
    classInput.addEventListener('change', () => {
        classFileList.innerHTML = '';
        clrErr('classFileError');
        if (classInput.files.length) {
            const chip = document.createElement('div');
            chip.className = 'file-chip';
            chip.innerHTML = `<i class="fa-solid fa-file"></i> ${esc(classInput.files[0].name)}`;
            classFileList.appendChild(chip);
        }
        validateFinalForm();
    });

    // ═══════════════════════════
    // MODULE FILES
    // ═══════════════════════════
    function parseMod(filename) {
        const base = filename.replace(/\.[^.]+$/, '');
        const sep  = base.indexOf('-');
        return sep !== -1
            ? { code: base.slice(0,sep).trim().toUpperCase(), name: base.slice(sep+1).trim() }
            : { code: '', name: base.trim() };
    }
    function syncModuleInput() {
        const dt = new DataTransfer();
        moduleFilesStore.forEach(m => dt.items.add(m.file));
        moduleInput.files = dt.files;
    }
    function rebuildModuleHidden() {
        hiddenModuleFields.innerHTML = '';
        moduleFilesStore.forEach((m,i) => {
            [['module_code_'+i, m.code],['module_name_'+i, m.name]].forEach(([n,v]) => {
                const inp = document.createElement('input');
                inp.type='hidden'; inp.name=n; inp.value=v;
                hiddenModuleFields.appendChild(inp);
            });
        });
    }
    function renderModulePreview() {
        modulePreviewBody.innerHTML = '';
        modulePreviewGroup.style.display = moduleFilesStore.length ? '' : 'none';
        if (!moduleFilesStore.length) return;
        moduleFilesStore.forEach((item, i) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><div class="file-name-cell"><i class="fa-solid fa-file"></i>
                    <span title="${esc(item.file.name)}">${esc(item.file.name)}</span></div></td>
                <td><input type="text" class="table-input mod-code" data-i="${i}"
                    value="${esc(item.code)}" placeholder="e.g. IT1123" maxlength="20"></td>
                <td><input type="text" class="table-input mod-name" data-i="${i}"
                    value="${esc(item.name)}" placeholder="Module name" maxlength="120"></td>
                <td class="actions-cell">
                    <button type="button" class="delete-file-btn mod-del" data-i="${i}">×</button>
                </td>`;
            modulePreviewBody.appendChild(row);
        });
        rebuildModuleHidden();
        modulePreviewBody.querySelectorAll('.mod-code').forEach(inp => {
            inp.addEventListener('input', function() {
                moduleFilesStore[+this.dataset.i].code = this.value.toUpperCase();
                rebuildModuleHidden();
            });
        });
        modulePreviewBody.querySelectorAll('.mod-name').forEach(inp => {
            inp.addEventListener('input', function() {
                moduleFilesStore[+this.dataset.i].name = this.value;
                rebuildModuleHidden();
            });
        });
        modulePreviewBody.querySelectorAll('.mod-del').forEach(btn => {
            btn.addEventListener('click', function() {
                moduleFilesStore.splice(+this.dataset.i, 1);
                syncModuleInput(); renderModulePreview(); validateFinalForm();
            });
        });
    }
    moduleInput.addEventListener('change', function() {
        clrErr('moduleFileError');
        const allowed = ['csv','xlsx','pdf'];
        Array.from(this.files).forEach(f => {
            const ext = f.name.split('.').pop().toLowerCase();
            if (!allowed.includes(ext)) { showErr('moduleFileError', `"${f.name}" is not supported.`); return; }
            if (!moduleFilesStore.some(m => m.file.name===f.name && m.file.size===f.size)) {
                const p = parseMod(f.name);
                moduleFilesStore.push({ file: f, code: p.code, name: p.name });
            }
        });
        syncModuleInput(); renderModulePreview(); validateFinalForm();
    });

    // ═══════════════════════════
    // INTENSITY / BREAK / DAYS
    // ═══════════════════════════
    document.querySelectorAll('.intensity-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.intensity-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            clrErr('intensityError'); validateFinalForm();
        });
    });
    document.querySelectorAll('.break-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.break-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            clrErr('breakError'); validateFinalForm();
        });
    });
    document.querySelectorAll('.day-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            pill.classList.toggle('selected');
            clrErr('studyDaysError'); validateFinalForm();
        });
    });
    [semesterStartDate, semesterEndDate, preferredStudyTime, sessionLength]
        .forEach(el => el.addEventListener('change', validateFinalForm));

    // ═══════════════════════════
    // ACCORDION (div headers)
    // ═══════════════════════════
    document.querySelectorAll('.acc-header').forEach(header => {
        header.addEventListener('click', function() {
            const body = this.nextElementSibling;
            const isOpen = body.classList.contains('open');
            body.classList.toggle('open', !isOpen);
            this.classList.toggle('open', !isOpen);
        });
    });

    // ═══════════════════════════
    // OCCUPIED TIMES
    // ═══════════════════════════
    function renderOccupied() {
        document.querySelectorAll('.occupied-item').forEach(el => el.remove());
        if (!occupiedTimesStore.length) {
            occupiedEmptyState.style.display = ''; return;
        }
        occupiedEmptyState.style.display = 'none';
        occupiedTimesStore.forEach((item, i) => {
            const div = document.createElement('div');
            div.className = 'occupied-item';
            div.innerHTML = `
                <span class="occ-badge">${esc(item.category)}</span>
                <span class="occ-title">${esc(item.title)}</span>
                <span class="occ-time">${esc(item.day_of_week)} · ${fmtTime(item.start_time)} – ${fmtTime(item.end_time)}</span>
                ${item.notes ? `<span class="occ-notes" title="${esc(item.notes)}">${esc(item.notes)}</span>` : ''}
                <button type="button" class="occ-del" data-i="${i}">×</button>`;
            occupiedList.appendChild(div);
        });
        document.querySelectorAll('.occ-del').forEach(btn => {
            btn.addEventListener('click', function() {
                occupiedTimesStore.splice(+this.dataset.i, 1);
                renderOccupied(); rebuildOccupiedHidden();
            });
        });
        rebuildOccupiedHidden();
    }
    function rebuildOccupiedHidden() {
        hiddenOccupiedFields.innerHTML = '';
        occupiedTimesStore.forEach((item, i) => {
            [['occupied_title_'+i,item.title],['occupied_category_'+i,item.category],
             ['occupied_day_'+i,item.day_of_week],['occupied_start_'+i,item.start_time],
             ['occupied_end_'+i,item.end_time],['occupied_notes_'+i,item.notes]
            ].forEach(([n,v]) => {
                const inp = document.createElement('input');
                inp.type='hidden'; inp.name=n; inp.value=v??'';
                hiddenOccupiedFields.appendChild(inp);
            });
        });
        const c = document.createElement('input');
        c.type='hidden'; c.name='occupied_count'; c.value=occupiedTimesStore.length;
        hiddenOccupiedFields.appendChild(c);
    }
    document.getElementById('addOccupiedBtn').addEventListener('click', () => {
        const err = document.getElementById('occupiedTimesError');
        err.textContent = '';
        const title = otTitle.value.trim(), start = otStart.value, end = otEnd.value;
        if (!title)       { err.textContent = 'Please enter a title.'; return; }
        if (!start)       { err.textContent = 'Please enter a start time.'; return; }
        if (!end)         { err.textContent = 'Please enter an end time.'; return; }
        if (start >= end) { err.textContent = 'End time must be after start time.'; return; }
        occupiedTimesStore.push({
            title, category: otCategory.value, day_of_week: otDay.value,
            start_time: start, end_time: end, notes: otNotes.value.trim()
        });
        renderOccupied();
        otTitle.value=''; otNotes.value=''; otStart.value=''; otEnd.value='';
    });
    document.getElementById('clearOccupiedBtn').addEventListener('click', () => {
        otTitle.value=''; otCategory.selectedIndex=0; otDay.selectedIndex=0;
        otStart.value=''; otEnd.value=''; otNotes.value='';
        document.getElementById('occupiedTimesError').textContent='';
    });

    // ═══════════════════════════
    // STUDY APPS
    // ═══════════════════════════
    function rebuildAppHidden() {
        hiddenStudyAppFields.innerHTML = '';
        studyAppsStore.forEach((a,i) => {
            [['study_app_name_'+i,a.name],['study_app_type_'+i,a.type],
             ['study_app_identifier_'+i,a.identifier],['study_app_purpose_'+i,a.purpose]
            ].forEach(([n,v]) => {
                const inp = document.createElement('input');
                inp.type='hidden'; inp.name=n; inp.value=v;
                hiddenStudyAppFields.appendChild(inp);
            });
        });
        const c = document.createElement('input');
        c.type='hidden'; c.name='study_app_count'; c.value=studyAppsStore.length;
        hiddenStudyAppFields.appendChild(c);
    }
    function renderAppTray() {
        document.querySelectorAll('.sel-app-tag').forEach(t => t.remove());
        if (!studyAppsStore.length) {
            trayPlaceholder.style.display = '';
            appCountBadge.style.display   = 'none';
        } else {
            trayPlaceholder.style.display = 'none';
            appCountBadge.style.display   = '';
            appCountBadge.textContent     = studyAppsStore.length;
            studyAppsStore.forEach(a => {
                const tag = document.createElement('div');
                tag.className = 'sel-app-tag';
                tag.dataset.id = a.identifier;
                tag.innerHTML  = `${esc(a.name)} <button type="button" class="tag-remove">×</button>`;
                tag.querySelector('.tag-remove').addEventListener('click', () => removeApp(a.identifier));
                selectedAppsTray.appendChild(tag);
            });
        }
        rebuildAppHidden(); validateFinalForm();
    }
    function addApp(app) {
        const name=( app.name||'').trim(), id=(app.identifier||'').trim();
        if (!name || !id) return;
        const err = document.getElementById('studyAppError');
        if (studyAppsStore.some(a => norm(a.identifier)===norm(id))) {
            err.textContent = `"${name}" is already in the list.`; return;
        }
        err.textContent = '';
        studyAppsStore.push({ name, type:(app.type||'desktop').trim(),
            typeLabel: typeLabel((app.type||'desktop').trim()),
            identifier: id, purpose:(app.purpose||'').trim() });
        renderAppTray();
    }
    function removeApp(identifier) {
        studyAppsStore = studyAppsStore.filter(a => norm(a.identifier) !== norm(identifier));
        // uncheck the chip if present
        document.querySelectorAll('.app-chip input[type="checkbox"]').forEach(cb => {
            if (norm(cb.dataset.identifier) === norm(identifier)) {
                cb.checked = false;
                cb.closest('.app-chip').classList.remove('checked');
            }
        });
        renderAppTray();
    }

    // Chip clicks
    document.querySelectorAll('.app-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            const cb = this.querySelector('input[type="checkbox"]');
            cb.checked = !cb.checked;
            this.classList.toggle('checked', cb.checked);
            if (cb.checked) {
                addApp({ name:cb.dataset.name, type:cb.dataset.type,
                         identifier:cb.dataset.identifier, purpose:cb.dataset.purpose });
            } else {
                removeApp(cb.dataset.identifier);
            }
        });
    });

    // Manual add
    document.getElementById('addStudyAppBtn').addEventListener('click', () => {
        const err = document.getElementById('studyAppError');
        const name=studyAppName.value.trim(), id=studyAppIdentifier.value.trim();
        if (!name || !id) { err.textContent='Please enter an app name and tracking match value.'; return; }
        addApp({ name, type:studyAppType.value, identifier:id, purpose:studyAppPurpose.value });
        if (!err.textContent) {
            studyAppName.value=''; studyAppIdentifier.value=''; studyAppPurpose.value='';
        }
    });
    document.getElementById('clearStudyAppInputsBtn').addEventListener('click', () => {
        studyAppName.value=''; studyAppIdentifier.value=''; studyAppPurpose.value='';
        document.getElementById('studyAppError').textContent='';
    });

    // ═══════════════════════════
    // REVIEW BUILDER
    // ═══════════════════════════
    const INTENSITY_MAP = {
        relaxed:'🌱 Just Keeping Up (~10–15 hrs/week)',
        balanced:'📖 Steady Progress (~16–25 hrs/week)',
        focused:'🔥 High Effort (~26–35 hrs/week)',
        intensive:'🚀 Full Grind (~36+ hrs/week)'
    };
    const BREAK_MAP = { short:'Short (5 min)', medium:'Medium (10–15 min)', long:'Long (20–30 min)' };

    function rr(key, val) {
        return `<div class="p-data-row"><span class="p-data-key">${esc(key)}</span><span class="p-data-val">${val}</span></div>`;
    }
    function buildReview() {
        const classFile = classInput.files.length ? classInput.files[0].name : null;
        document.getElementById('reviewFilesBody').innerHTML =
            rr('Class timetable', classFile
                ? `<span style="color:#15803d">${esc(classFile)}</span>`
                : '<span style="color:#dc2626">Not uploaded</span>') +
            rr('Module files', moduleFilesStore.length
                ? `${moduleFilesStore.length} file${moduleFilesStore.length!==1?'s':''}` : '<span style="color:#dc2626">None</span>') +
            rr('Semester', `${esc(semesterStartDate.value||'—')} &rarr; ${esc(semesterEndDate.value||'—')}`);

        const intVal   = document.querySelector('input[name="study_intensity"]:checked')?.value;
        const breakVal = document.querySelector('input[name="break_preference"]:checked')?.value;
        const selSessEl = sessionLength.options[sessionLength.selectedIndex];
        const selTimeEl = preferredStudyTime.options[preferredStudyTime.selectedIndex];
        document.getElementById('reviewStyleBody').innerHTML =
            rr('Intensity',  esc(INTENSITY_MAP[intVal]||'—')) +
            rr('Study time', esc(selTimeEl?.value ? selTimeEl.text : '—')) +
            rr('Session',    esc(selSessEl?.value ? selSessEl.text : '—')) +
            rr('Break',      esc(BREAK_MAP[breakVal]||'—')) +
            rr('Study days', '<div class="p-tags"><span class="p-badge p-badge-primary">Everyday (Mon-Sun)</span></div>');

        document.getElementById('reviewCommitmentsBody').innerHTML = occupiedTimesStore.length
            ? occupiedTimesStore.map(it => `
                <div class="p-commitment">
                    <div class="p-comm-head">
                        <span class="p-comm-title">${esc(it.title)}</span>
                        <span class="p-comm-time">${esc(it.day_of_week)} &middot; ${fmtTime(it.start_time)} – ${fmtTime(it.end_time)}</span>
                    </div>
                    ${it.notes ? `<div class="p-comm-note">${esc(it.notes)}</div>` : ''}
                </div>`).join('')
            : '<p class="p-empty">No recurring blocks added.</p>';

        document.getElementById('reviewAppsBody').innerHTML = studyAppsStore.length
            ? `<div class="p-tags">${
                studyAppsStore.map(a=>`<span class="p-badge p-badge-app"><i class="fa-solid fa-cube" style="margin-right:5px; color:#94a3b8"></i>${esc(a.name)}</span>`).join('')}</div>`
            : '<p class="p-empty">No study apps selected.</p>';

        validateFinalForm();
    }

    // ═══════════════════════════
    // INIT
    // ═══════════════════════════
    renderOccupied();
    renderAppTray();
    validateFinalForm();

    // ═══════════════════════════
    // FORM SUBMISSION (MODAL)
    // ═══════════════════════════
    document.getElementById('studyPlanForm').addEventListener('submit', function(e) {
        // Show the processing modal
        document.getElementById('processingModalOverlay').style.display = 'flex';
        
        // Visual progress simulation
        setTimeout(() => {
            // Step 1 done (Uploading), move to Step 2 (Extracting) - Takes approx 1 minute
            document.getElementById('procStep1').classList.remove('active');
            document.getElementById('procStep1').classList.add('completed');
            document.getElementById('procStep2').classList.add('active');
        }, 60000);

        setTimeout(() => {
            // Step 2 done (Extracting), move to Step 3 (Saving) - Takes approx another minute
            document.getElementById('procStep2').classList.remove('active');
            document.getElementById('procStep2').classList.add('completed');
            document.getElementById('procStep3').classList.add('active');
        }, 120000); // 2 minutes total elapsed, rest of the 4 mins is spent on Step 3
    });

    // ═══════════════════════════
    // TOGGLE UPLOAD WIZARD
    // ═══════════════════════════
    const showWizardBtn = document.getElementById('showUploadWizardBtn');
    if (showWizardBtn) {
        showWizardBtn.addEventListener('click', function() {
            const detailedSummary = document.getElementById('detailedSavedSummary');
            const wizardContainer = document.getElementById('uploadWizardContainer');
            if (detailedSummary) detailedSummary.style.display = 'none';
            if (wizardContainer) {
                wizardContainer.style.display = 'block';
                wizardContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
});