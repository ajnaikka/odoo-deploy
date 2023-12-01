$(document).ready(function() {

      var owl = $("#owl-demo-test");

      owl.owlCarousel({

          itemsCustom : [
            [0, 1],
            [450, 1],
            [600, 1],
            [700, 2],
            [1000, 2],
            [1200, 2],
            [1400, 2],
            [1600, 2]
          ],
          navigation : false,
		  slideSpeed : 400,
          paginationSpeed : 400,
		  autoPlay : 300000,
          stopOnHover : true,
          paginationSpeed : 1000,
          goToFirstSpeed : 2000,


      });

    });