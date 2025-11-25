// app.js
App({
  globalData: {
    baseUrl: 'http://localhost:3000/api', // 开发环境
    // baseUrl: 'https://api.yuebei.com/api', // 生产环境
    mapKey: '', // 腾讯地图key
    currentGathering: null,
    userInfo: {
      tempId: '',
      nickname: '',
      location: null
    }
  },
  
  onLaunch() {
    // 生成临时用户ID
    this.globalData.userInfo.tempId = this.generateTempId();
    
    // 获取系统信息
    const systemInfo = wx.getSystemInfoSync();
    this.globalData.systemInfo = systemInfo;
    
    // 检查位置权限
    this.checkLocationPermission();
  },
  
  generateTempId() {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  },
  
  checkLocationPermission() {
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.userLocation']) {
          // 引导用户开启定位权限
          console.log('需要请求定位权限');
        }
      }
    });
  },
  
  // 通用请求方法
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.globalData.baseUrl + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'content-type': 'application/json',
          'x-temp-user-id': this.globalData.userInfo.tempId
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            reject(res);
          }
        },
        fail: reject
      });
    });
  }
});