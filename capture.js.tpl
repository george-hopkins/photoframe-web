var page = require('webpage').create();

page.viewportSize = { width: 800, height: 600 };
page.clipRect = { top: 0, left: 0, width: 800, height: 600 };

page.open({{!url}}, function() {
  window.setTimeout(function () {
    page.render({{!output}}, { quality: 98 });
    phantom.exit();
  }, {{!wait}});
});
