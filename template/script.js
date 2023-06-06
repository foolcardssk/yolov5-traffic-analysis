function Dropfunction(){
    var navbar=document.getElementById('nav');
    navbar.classList.toggle('show');
    }
    function scrollToTop() {
    document.documentElement.scrollTo({
        top: 0,
        behavior: "smooth"
    });
    }

    function initMap() {
        var locations = [
            { lat: 49.919943, lng: 8.611070, title: 'Weiterstadt'},
        ];

        var map = new google.maps.Map(document.getElementById('map'), {
            zoom: 12,
            center: { lat: 49.919943, lng: 8.611070 },
            mapTypeId: google.maps.MapTypeId.TERRAIN,
        });

        for (var i = 0; i < locations.length; i++) {
            createMarker(locations[i], map);
        }
        }

        function createMarker(location, map) {
        var marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.title
        });

        var vidvr = document.getElementById('status-cards');
        // Attach click event listener to each marker
        marker.addListener('click', function () {
            vidvr.style.display="grid"
        });
    }

function fetchData() {
    var a1v = document.getElementById('veh-cnt1')
    var a2v = document.getElementById('veh-cnt2')
    var a1d = document.getElementById('trf-level1')
    var a2d = document.getElementById('trf-level2')
    var sm = document.getElementById('tot-cnt')
    fetch('output.json')
      .then(response => response.json())
      .then(data => {
        const a1 = data.a1;
        const a2 = data.a2;
        const sum = a1 + a2;
        const a1Density = data.a1_density;
        const a2Density = data.a2_density;

        a1v.textContent=a1
        a2v.textContent=a2
        a1d.textContent=a1Density
        a2d.textContent=a2Density
        sm.textContent=sum

        if((a1Density==="Low")&&(a2Density==="Low")){
            a1d.style.color="Green"
            a2d.style.color="Green"
        }
      })
      .catch(error => console.error('Error:', error));
  }
  
  setInterval(fetchData, 2000);
  