// static/js/velki_header.js
(function(){
  // Mobile toggle
  var toggle = document.getElementById('velki-mobile-toggle');
  var mobileMenu = document.getElementById('velki-mobile-menu');
  toggle && toggle.addEventListener('click', function(){
    if(mobileMenu.style.display === 'block'){
      mobileMenu.style.display = 'none';
      toggle.classList.remove('open');
    } else {
      mobileMenu.style.display = 'block';
      toggle.classList.add('open');
    }
  });

  // Sticky header small shrink effect
  var header = document.getElementById('velki-header');
  var lastScroll = 0;
  window.addEventListener('scroll', function(){
    var sc = window.scrollY || window.pageYOffset;
    if(sc > 40){
      header.classList.add('velki-header-scrolled');
    } else {
      header.classList.remove('velki-header-scrolled');
    }
    lastScroll = sc;
  });

  // WhatsApp quick button
  var waBtn = document.getElementById('velki-wa-btn');
  if(waBtn){
    waBtn.addEventListener('click', function(e){
      e.preventDefault();
      var g = window.VELKI_GLOBAL_WHATSAPP || '';
      if(!g){
        alert('WhatsApp number not set');
        return;
      }
      window.open('https://wa.me/' + g, '_blank');
    });
  }

})();

