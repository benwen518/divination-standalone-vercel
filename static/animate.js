// 简易 FLIP 布局动画：当容器内子元素位置/尺寸变化时，平滑过渡到新位置
// 用法：animateChildren(container, 320, 'ease-out')

(function () {
  function getItemInfos(container) {
    return Array.from(container.children).map(function (el) {
      var rect = el.getBoundingClientRect();
      return {
        element: el,
        x: rect.left,
        y: rect.top,
        width: rect.width,
        height: rect.height,
      };
    });
  }

  function animateItems(oldItems, newItems, duration, easing) {
    for (var i = 0; i < newItems.length; i++) {
      var newItem = newItems[i];
      var el = newItem.element;
      if ((el.className || '').indexOf('ignore-animate') !== -1) continue;

      var oldItem = null;
      for (var j = 0; j < oldItems.length; j++) {
        if (oldItems[j].element === el) {
          oldItem = oldItems[j];
          break;
        }
      }
      if (!oldItem) {
        oldItem = {
          element: el,
          x: newItem.x,
          y: newItem.y,
          width: newItem.width / 1.5,
          height: newItem.height / 1.5,
        };
      }

      var translateX = oldItem.x - newItem.x;
      var translateY = oldItem.y - newItem.y;
      var scaleX = oldItem.width / newItem.width;
      var scaleY = oldItem.height / newItem.height;

      if (translateX === 0 && translateY === 0 && scaleX === 1 && scaleY === 1) continue;

      el.animate(
        [
          { transform: 'translate(' + translateX + 'px, ' + translateY + 'px) scale(' + scaleX + ', ' + scaleY + ')' },
          { transform: 'none' },
        ],
        { duration: duration, easing: easing }
      );
    }
  }

  function animateChildren(container, duration, easing) {
    if (!container) return null;
    var _duration = typeof duration === 'number' ? duration : 300;
    var _easing = typeof easing === 'string' ? easing : 'ease-out';

    var oldItemInfos = getItemInfos(container);

    var observer = new MutationObserver(function () {
      var newItemInfos = getItemInfos(container);
      if (oldItemInfos) {
        animateItems(oldItemInfos, newItemInfos, _duration, _easing);
      }
      oldItemInfos = newItemInfos;
    });
    observer.observe(container, { childList: true });
    return observer;
  }

  // 暴露到全局
  window.animateChildren = animateChildren;
})();


