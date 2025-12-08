(() => {
  if (typeof window !== 'undefined') {
    if (!('ResizeObserver' in window)) {
      class ResizeObserverShim {
        constructor(callback) {
          this._cb = typeof callback === 'function' ? callback : () => {}
        }
        observe() {}
        unobserve() {}
        disconnect() {}
      }
      window.ResizeObserver = ResizeObserverShim
    }
  }
})()

