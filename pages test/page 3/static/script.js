$(document).ready(function () {
    var pageSize = 20;
    var currentPage = 1;
    var totalProducts = 0;
    var totalPages = 0;
    var allProducts = [];
    var filteredProducts = null;

    // Cargar la lista de productos desde la base de datos al inicio
    loadProductsFromDatabase();

    function loadProductsFromDatabase() {
        $.ajax({
            type: "GET",
            url: "/get_products",
            dataType: "json",
            success: function (data) {
                allProducts = data;
                allProducts = orderByPriceAscending(allProducts)
                totalProducts = allProducts.length;
                totalPages = Math.ceil(totalProducts / pageSize);

                // Manejar el evento de escritura en el campo de búsqueda
                $('#search').on('input', function () {
                    currentPage = 1;
                    var searchTerm = $(this).val().toLowerCase();
                    var searchTermsArray = searchTerm.split(' ').filter(Boolean);
                    filteredProducts = allProducts.filter(function (product) {
                        return searchTermsArray.every(function (term) {
                            return product.description.toLowerCase().includes(term);
                        });
                    });

                    // Mover la barra de búsqueda hacia arriba al buscar
                    $('.search-box').addClass('search-box-active');

                    // Mostrar los resultados después de cargar la imagen
                    setTimeout(function () {
                        displayPage(currentPage, filteredProducts);
                    }, 100);
                });

                // Mostrar solo el cuadro de búsqueda al inicio
                displaySearchBoxOnly();
            },
            error: function (error) {
                console.error("Error al cargar los datos desde la base de datos:", error);
            }
        });
    }
    // Manejar el evento de clic en el botón de búsqueda
    $('#search-btn').on('click', function () {
        // Remueve la clase inicial y agrega la clase activa
        $('.search-box').removeClass('search-box-initial');
        $('.search-box').addClass('search-box-active');
        
        // Mueve la barra hacia arriba
        $('.search-box').css('margin-top', '50px');
        
    });
    
    function displaySearchBoxOnly() {
        // Ocultar resultados y mostrar solo el cuadro de búsqueda
        $('#results-container').empty();
        $('#next-page-btn').hide();
        $('#pagination-info').hide();
        $('#unavailable-txt').text('');
        $('.search-box').removeClass('search-box-active');
        updatePaginationInfo();
    }

    function orderByPriceAscending(products) {

        // Copia del arreglo
        const productsCopy = products.slice();

        productsCopy.forEach(function (product) {
            product.price = parsePrice(product.price);
        });

        const sortedProducts = productsCopy.sort((a, b) => a.price - b.price);
        console.log(sortedProducts)
        return sortedProducts;
    }
    
    function parsePrice(priceString) {
        if (typeof priceString === 'number') {
            return priceString;
        }
    
        var cleanedPrice = priceString.replace(/[^\d.,]/g, '');
        cleanedPrice = cleanedPrice.replace('$', '').replace('.', '').replace(',', '.');
    
        const parsedPrice = parseFloat(cleanedPrice);
    
        return isNaN(parsedPrice) ? 0 : parsedPrice;
    }

    function displayPage(pageNumber, products) {
        var resultsContainer = $('#results-container');
        var unavailableTxt = $('#unavailable-txt');
        var paginationContainer = $('#pagination-container');
        var paginationInfo = $('#pagination-info');

        resultsContainer.empty();
        var startIdx = (pageNumber - 1) * pageSize;
        var endIdx = startIdx + pageSize;
        var currentProducts = products.slice(startIdx, endIdx);
        resultsContainer.empty();
        
        if (currentProducts.length > 0) {
            currentProducts.forEach(function (product) {
                var resultItem = $('<div class="card"></div>');
                var imgElement = $('<img alt="' + product.description + '">');

                imgElement.on('load', function () {
                    resultItem.append(imgElement);
                    resultItem.append('<h3>' + product.description + '</h3>');
                    resultItem.append('<p>Price: ' + product.price + '</p>');

                    if (product.brand) {
                        resultItem.append('<p>Brand: ' + product.brand + '</p>');
                    }

                    resultsContainer.append(resultItem);
                });

                imgElement.attr('src', product.image);
            });

            unavailableTxt.text('');
            paginationContainer.show();
            paginationInfo.show()
            updatePaginationInfo();

            if (currentPage < totalPages) {
                $('#next-page-btn').show();
            } else {
                $('#next-page-btn').hide();
            }
        } else {
            unavailableTxt.text('No hay productos disponibles.');
            paginationContainer.hide();
        }
    }

    function updatePaginationInfo() {
        // Actualiza la información de paginación
        var total = (filteredProducts ? filteredProducts.length : totalProducts);
        totalPages = Math.ceil(total / pageSize);
        $('#pagination-info').text('Mostrando página ' + currentPage + ' de ' + totalPages);
    }

    // Manejar el clic en el botón de siguiente página
    $('#next-page-btn').on('click', function () {
        if (currentPage < totalPages) {
            currentPage++;
            if (filteredProducts) {
                displayPage(currentPage, filteredProducts);
            } else {
                displayPage(currentPage, allProducts);
            }
        }
    });
    
});
