/* Legacy frontend script (no @odoo-module) */
(function () {
    'use strict';

    var WIDGET_IDS = [
        'brand_selector',
        'model_selector',
        'year_selector',
        'series_selector',
        'variant_selector',
        'search_btn',
        'my_vehicle_btn',
    ];

    function isVehicleWidgetElement(el) {
        if (!el || !el.id) return false;
        return WIDGET_IDS.indexOf(el.id) !== -1;
    }

    function callAPI(url, params) {
        params = params || {};
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: params,
                id: null,
            }),
        }).then(function (res) {
            if (!res.ok) {
                return res.text().then(function (t) {
                    throw new Error(t || res.statusText);
                });
            }
            return res.json();
        });
    }

    function populate(select, data, placeholder) {
        if (!select) return;

        select.innerHTML = '<option value="">' + placeholder + '</option>';

        if (!Array.isArray(data)) return;

        data.forEach(function (item) {
            var option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            select.appendChild(option);
        });
    }

    // =============================
    // BOOTSTRAP MODAL HELPER
    // =============================
    function showModal(modalId) {
        var modalEl = document.getElementById(modalId);
        if (!modalEl) return;

        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            var modal = new bootstrap.Modal(modalEl);
            modal.show();
        } else {
            // Fallback: use simple show/hide if Bootstrap not available
            modalEl.style.display = 'block';
            modalEl.classList.add('show');
            document.body.classList.add('modal-open');
            
            // Create backdrop
            var backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.id = modalId + '_backdrop';
            document.body.appendChild(backdrop);
        }
    }

    function hideModal(modalId) {
        var modalEl = document.getElementById(modalId);
        if (!modalEl) return;

        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            var modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
                modal.hide();
            }
        } else {
            // Fallback: use simple show/hide
            modalEl.style.display = 'none';
            modalEl.classList.remove('show');
            document.body.classList.remove('modal-open');
            
            var backdrop = document.getElementById(modalId + '_backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        }
    }

    function initVehicleFilter() {

        var brand = document.getElementById('brand_selector');
        var model = document.getElementById('model_selector');
        var year = document.getElementById('year_selector');
        var series = document.getElementById('series_selector');
        var variant = document.getElementById('variant_selector');
        var searchBtn = document.getElementById('search_btn');
        var myVehicleBtn = document.getElementById('my_vehicle_btn');
        var vehicleModal = document.getElementById('vehicleModal');
        var selectedPathDiv = document.getElementById('selected_path');
        var pathDisplay = document.getElementById('path_display');
        var clearPathBtn = document.getElementById('clear_path_btn');

        // If the main widget elements are not present, don't proceed
        if (!brand && !myVehicleBtn) {
            return;
        }

        // =============================
        // PATH DISPLAY LOGIC
        // =============================
        function updatePathDisplay() {
            if (!pathDisplay || !selectedPathDiv) return;

            var items = [];
            if (brand && brand.value) items.push(brand.options[brand.selectedIndex].text);
            if (model && model.value) items.push(model.options[model.selectedIndex].text);
            if (year && year.value) items.push(year.options[year.selectedIndex].text);
            if (series && series.value) items.push(series.options[series.selectedIndex].text);
            if (variant && variant.value) items.push(variant.options[variant.selectedIndex].text);

            if (items.length > 0) {
                pathDisplay.innerHTML = '';
                items.forEach(function(text, index) {
                    var span = document.createElement('span');
                    span.className = 'path-item';
                    span.textContent = text;
                    pathDisplay.appendChild(span);
                    
                    if (index < items.length - 1) {
                        var icon = document.createElement('i');
                        icon.className = 'fa fa-chevron-right path-sep';
                        pathDisplay.appendChild(icon);
                    }
                });
                selectedPathDiv.style.display = 'block';
                
                // Store path in session storage to persist after page reload
                sessionStorage.setItem('vehicle_search_path', JSON.stringify({
                    html: pathDisplay.innerHTML,
                    params: {
                        brand: brand.value,
                        model: model.value,
                        year: year.value,
                        series: series.value,
                        variant: variant.value
                    }
                }));
            } else {
                selectedPathDiv.style.display = 'none';
                sessionStorage.removeItem('vehicle_search_path');
            }
        }

        // Restore path from session storage on load
        var savedPath = sessionStorage.getItem('vehicle_search_path');
        if (savedPath && pathDisplay && selectedPathDiv) {
            try {
                var data = JSON.parse(savedPath);
                // Only show if we are on a shop page with 'products' param (meaning a search was performed)
                var urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('products')) {
                    pathDisplay.innerHTML = data.html;
                    selectedPathDiv.style.display = 'block';
                }
            } catch(e) {}
        }

        if (clearPathBtn) {
            clearPathBtn.addEventListener('click', function() {
                sessionStorage.removeItem('vehicle_search_path');
                window.location.href = '/shop';
            });
        }

        // prevent form submit
        var widgetRoot = brand && brand.closest('.o_vehicle_compat_filter');
        if (widgetRoot) {
            var shopForm = widgetRoot.closest('form');
            if (shopForm) {
                shopForm.addEventListener('submit', function (ev) {
                    var a = document.activeElement;
                    if (isVehicleWidgetElement(a)) {
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                }, true);
            }
        }

        function bindEnterNoSubmit(el) {
            if (!el) return;
            el.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter') {
                    ev.preventDefault();
                    ev.stopPropagation();
                }
            });
        }

        bindEnterNoSubmit(brand);
        bindEnterNoSubmit(model);
        bindEnterNoSubmit(year);
        bindEnterNoSubmit(series);
        bindEnterNoSubmit(variant);

        if (brand) brand.disabled = true;

        // =============================
        // LOAD DATA
        // =============================
        function loadBrands() {
            if (!brand) return;
            return callAPI('/shop/vehicle/brands', {})
                .then(function (data) {
                    var result = data.result || data;
                    populate(brand, result, 'Select Brand');
                    brand.disabled = false;
                    return result;
                })
                .catch(function (err) {
                    console.error('Failed to load brands:', err);
                    populate(brand, [], 'Select Brand');
                    brand.disabled = false;
                });
        }

        function loadModels(brandId) {
            if (!model) return;
            return callAPI('/shop/vehicle/models', { brand_id: brandId })
                .then(function (data) {
                    var result = data.result || data;
                    populate(model, result, 'Select Model');
                    model.disabled = false;
                    return result;
                })
                .catch(function (err) {
                    console.error('Failed to load models:', err);
                    populate(model, [], 'Select Model');
                    model.disabled = false;
                });
        }

        function loadYears(modelId) {
            if (!year) return;
            return callAPI('/shop/vehicle/years', { model_id: modelId })
                .then(function (data) {
                    var result = data.result || data;
                    populate(year, result, 'Select Year');
                    year.disabled = false;
                    return result;
                })
                .catch(function (err) {
                    console.error('Failed to load years:', err);
                    populate(year, [], 'Select Year');
                    year.disabled = false;
                });
        }

        function loadSeries(yearId) {
            if (!series) return;
            return callAPI('/shop/vehicle/series', { year_id: yearId })
                .then(function (data) {
                    var result = data.result || data;
                    populate(series, result, 'Select Series');
                    series.disabled = false;
                    return result;
                })
                .catch(function (err) {
                    console.error('Failed to load series:', err);
                    populate(series, [], 'Select Series');
                    series.disabled = false;
                });
        }

        function loadVariants(seriesId) {
            if (!variant) return;
            return callAPI('/shop/vehicle/variants', { series_id: seriesId })
                .then(function (data) {
                    var result = data.result || data;
                    populate(variant, result, 'Select Variant');
                    variant.disabled = false;
                    return result;
                })
                .catch(function (err) {
                    console.error('Failed to load variants:', err);
                    populate(variant, [], 'Select Variant');
                    variant.disabled = false;
                });
        }

        function resetFrom(level) {
            var order = ['model', 'year', 'series', 'variant'];
            var index = order.indexOf(level);

            for (var i = index; i < order.length; i++) {
                var el = document.getElementById(order[i] + '_selector');
                if (el) {
                    el.innerHTML = '<option value="">Select ' + order[i].charAt(0).toUpperCase() + order[i].slice(1) + '</option>';
                    el.disabled = true;
                }
            }
        }

        // =============================
        // CHANGE EVENTS
        // =============================
        if (brand) {
            brand.addEventListener('change', function () {
                resetFrom('model');
                if (this.value) loadModels(this.value);
            });
        }

        if (model) {
            model.addEventListener('change', function () {
                resetFrom('year');
                if (this.value) loadYears(this.value);
            });
        }

        if (year) {
            year.addEventListener('change', function () {
                resetFrom('series');
                if (this.value) loadSeries(this.value);
            });
        }

        if (series) {
            series.addEventListener('change', function () {
                resetFrom('variant');
                if (this.value) loadVariants(this.value);
            });
        }

        // =============================
        // 🔥 SEARCH LOGIC
        // =============================
        function performSearch(params) {
            // Update path display before redirecting
            updatePathDisplay();
            
            callAPI('/shop/vehicle/search', params)
                .then(function (data) {
                    var result = data.result || data;
                    if (result.products && Array.isArray(result.products)) {
                        var url = new URL(window.location.origin + '/shop');
                        if (result.products.length > 0) {
                            url.searchParams.set('products', result.products.join(','));
                        } else {
                            url.searchParams.set('products', '0');
                        }
                        window.location.href = url.toString();
                    } else if (result.error) {
                        alert('Search error: ' + result.error);
                    }
                })
                .catch(function (err) {
                    console.error('Search failed:', err);
                    alert('Search failed. Please try again.');
                });
        }

        // =============================
        // 🔥 MY VEHICLE BUTTON - LOAD VEHICLES
        // =============================
        if (myVehicleBtn && vehicleModal) {
            myVehicleBtn.addEventListener('click', function (ev) {
                ev.preventDefault();
                ev.stopPropagation();

                // Show loading state
                var loadingDiv = document.getElementById('vehicle_loading');
                var listContainer = document.getElementById('vehicle_list_container');
                var emptyState = document.getElementById('vehicle_empty_state');
                var tbody = document.getElementById('vehicle_list_body');

                if (loadingDiv) loadingDiv.style.display = 'block';
                if (listContainer) listContainer.style.display = 'none';
                if (emptyState) emptyState.style.display = 'none';

                // Show modal
                showModal('vehicleModal');

                callAPI('/shop/user/vehicles', {})
                    .then(function (data) {
                        var vehicles = data.result || data;
                        if (loadingDiv) loadingDiv.style.display = 'none';

                        if (!vehicles || !Array.isArray(vehicles)) {
                            vehicles = [];
                        }

                        if (!vehicles.length) {
                            if (emptyState) emptyState.style.display = 'block';
                            if (listContainer) listContainer.style.display = 'none';
                            return;
                        }

                        if (listContainer) listContainer.style.display = 'block';
                        if (tbody) {
                            tbody.innerHTML = '';
                            vehicles.forEach(function (v) {
                                var tr = document.createElement('tr');
                                tr.innerHTML = '<td>' + (v.brand_name || '-') + '</td>' +
                                    '<td>' + (v.model_name || '-') + '</td>' +
                                    '<td class="text-end">' +
                                    '<button class="btn btn-primary btn-sm select_vehicle" ' +
                                    'data-brand-name="' + (v.brand_name || '') + '" ' +
                                    'data-model-name="' + (v.model_name || '') + '" ' +
                                    'data-brand-id="' + (v.brand_id || '') + '" ' +
                                    'data-model-id="' + (v.model_id || '') + '" ' +
                                    'data-year-id="' + (v.year_id || '') + '" ' +
                                    'data-series-id="' + (v.series_id || '') + '" ' +
                                    'data-variant-id="' + (v.variant_id || '') + '" ' +
                                    'data-comp-brand-id="' + (v.comp_brand_id || '') + '" ' +
                                    'data-comp-model-id="' + (v.comp_model_id || '') + '" ' +
                                    'data-comp-year-id="' + (v.comp_year_id || '') + '" ' +
                                    'data-comp-series-id="' + (v.comp_series_id || '') + '" ' +
                                    'data-comp-variant-id="' + (v.comp_variant_id || '') + '">' +
                                    'Select</button></td>';
                                tbody.appendChild(tr);
                            });

                            // Bind select buttons
                            tbody.querySelectorAll('.select_vehicle').forEach(function (btn) {
                                btn.addEventListener('click', function () {
                                    var compBrandId = this.getAttribute('data-comp-brand-id');
                                    
                                    // 1. If compatibility exists, use IDs directly (most robust)
                                    if (compBrandId && compBrandId !== 'false' && compBrandId !== '') {
                                        var bId = compBrandId;
                                        var mId = this.getAttribute('data-comp-model-id');
                                        var yId = this.getAttribute('data-comp-year-id');
                                        var sId = this.getAttribute('data-comp-series-id');
                                        var vId = this.getAttribute('data-comp-variant-id');
                                        
                                        hideModal('vehicleModal');
                                        
                                        if (!brand) {
                                            performSearch({ brand_id: bId, model_id: mId, year_id: yId, series_id: sId, variant_id: vId });
                                            return;
                                        }

                                        // Auto-fill dropdowns via Promise chain
                                        brand.value = bId;
                                        resetFrom('model');
                                        var chain = Promise.resolve();
                                        if (mId && mId !== 'false') {
                                            chain = chain.then(function() { return loadModels(bId).then(function() { model.value = mId; resetFrom('year'); }); });
                                            if (yId && yId !== 'false') {
                                                chain = chain.then(function() { return loadYears(mId).then(function() { year.value = yId; resetFrom('series'); }); });
                                                if (sId && sId !== 'false') {
                                                    chain = chain.then(function() { return loadSeries(yId).then(function() { series.value = sId; resetFrom('variant'); }); });
                                                    if (vId && vId !== 'false') {
                                                        chain = chain.then(function() { return loadVariants(sId).then(function() { variant.value = vId; }); });
                                                    }
                                                }
                                            }
                                        }
                                        chain.then(function() { performSearch({ brand_id: bId, model_id: mId, year_id: yId, series_id: sId, variant_id: vId }); });
                                        return;
                                    }

                                    // 2. Fallback to original working logic (Name-based matching for vehicle fields)
                                    var bName = this.getAttribute('data-brand-name');
                                    var mName = this.getAttribute('data-model-name');
                                    var bId = this.getAttribute('data-brand-id');
                                    var mId = this.getAttribute('data-model-id');
                                    var yId = this.getAttribute('data-year-id');
                                    var sId = this.getAttribute('data-series-id');
                                    var vId = this.getAttribute('data-variant-id');

                                    if (!brand) {
                                        hideModal('vehicleModal');
                                        performSearch({ brand_id: bId, model_id: mId, year_id: yId, series_id: sId, variant_id: vId });
                                        return;
                                    }

                                    function findOptionByText(select, text) {
                                        if (!select || !text) return null;
                                        var options = select.options;
                                        for (var i = 0; i < options.length; i++) {
                                            if (options[i].text.trim().toLowerCase() === text.trim().toLowerCase()) {
                                                return options[i].value;
                                            }
                                        }
                                        return null;
                                    }

                                    var brandValue = findOptionByText(brand, bName);
                                    if (brandValue) {
                                        brand.value = brandValue;
                                        resetFrom('model');
                                        loadModels(brandValue).then(function() {
                                            var modelValue = findOptionByText(model, mName);
                                            if (modelValue) {
                                                model.value = modelValue;
                                                hideModal('vehicleModal');
                                                if (searchBtn) searchBtn.click();
                                            } else {
                                                alert('Error: Model "' + mName + '" not found in the list for brand "' + bName + '".');
                                            }
                                        });
                                    } else {
                                        alert('Error: Brand "' + bName + '" not found in the list.');
                                    }
                                });
                            });
                        }
                    })
                    .catch(function (err) {
                        console.error('Failed to load user vehicles:', err);
                        if (loadingDiv) loadingDiv.style.display = 'none';
                        if (emptyState) emptyState.style.display = 'block';
                    });
            });
        }

        // =============================
        // SEARCH BUTTON
        // =============================
        if (searchBtn) {
            searchBtn.addEventListener('click', function () {
                var b = brand ? brand.value : '';
                var m = model ? model.value : '';
                var y = year ? year.value : '';
                var s = series ? series.value : '';
                var v = variant ? variant.value : '';

                if (!b) {
                    alert('Please select at least a brand.');
                    return;
                }

                performSearch({
                    brand_id: b,
                    model_id: m,
                    year_id: y,
                    series_id: s,
                    variant_id: v
                });
            });
        }

        // INIT
        loadBrands();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVehicleFilter);
    } else {
        initVehicleFilter();
    }

})();
