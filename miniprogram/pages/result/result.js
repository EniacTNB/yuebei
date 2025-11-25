// pages/result/result.js
const app = getApp()

Page({
  data: {
    code: '',
    isCreator: false,
    gathering: null,
    recommendations: [],
    isLoading: true,
    shareVisible: false
  },

  onLoad(options) {
    if (options.code) {
      this.setData({ 
        code: options.code,
        isCreator: options.isCreator === 'true'
      })
      
      // 加载聚会信息和推荐结果
      this.loadGathering(options.code)
      this.loadRecommendations(options.code)
    }
  },

  onShow() {
    // 页面显示时刷新数据
    if (this.data.code) {
      this.loadGathering(this.data.code)
      this.loadRecommendations(this.data.code)
    }
  },

  // 加载聚会信息
  loadGathering(code) {
    wx.request({
      url: app.globalData.baseUrl + '/gathering/' + code,
      success: (res) => {
        if (res.data.success) {
          this.setData({ gathering: res.data.data })
        }
      }
    })
  },

  // 加载推荐结果
  loadRecommendations(code) {
    this.setData({ isLoading: true })
    
    wx.request({
      url: app.globalData.baseUrl + '/recommend/calculate',
      method: 'POST',
      data: {
        gathering_code: code,
        preferences: {}
      },
      success: (res) => {
        if (res.data.success) {
          this.setData({ 
            recommendations: res.data.data || [],
            isLoading: false
          })
        } else {
          // 如果还没有推荐结果，使用模拟数据
          this.loadMockRecommendations(code)
        }
      },
      fail: () => {
        // 失败时加载模拟数据
        this.loadMockRecommendations(code)
      }
    })
  },

  // 加载模拟推荐数据
  loadMockRecommendations(code) {
    wx.request({
      url: app.globalData.baseUrl + '/recommend/mock/' + code,
      success: (res) => {
        if (res.data.success) {
          this.setData({ 
            recommendations: res.data.data || [],
            isLoading: false
          })
        }
      },
      fail: () => {
        this.setData({ isLoading: false })
      }
    })
  },

  // 刷新推荐
  refreshRecommendations() {
    wx.showLoading({ title: '刷新中...' })
    
    wx.request({
      url: app.globalData.baseUrl + '/recommend/refresh/' + this.data.code,
      method: 'POST',
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          this.setData({ 
            recommendations: res.data.data || []
          })
          wx.showToast({
            title: '刷新成功',
            icon: 'success'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '刷新失败',
          icon: 'none'
        })
      }
    })
  },

  // 查看地点详情
  viewDetail(e) {
    const { index } = e.currentTarget.dataset
    const place = this.data.recommendations[index]
    
    // 这里可以跳转到详情页或显示弹窗
    wx.showModal({
      title: place.name,
      content: `地址：${place.address}\n评分：${place.rating || '暂无'}\n平均通勤：${place.avg_travel_time}分钟`,
      confirmText: '导航',
      success: (res) => {
        if (res.confirm) {
          this.navigate(place)
        }
      }
    })
  },

  // 导航到地点
  navigate(place) {
    wx.openLocation({
      latitude: place.location.lat,
      longitude: place.location.lng,
      name: place.name,
      address: place.address,
      scale: 18
    })
  },

  // 显示分享面板
  showShare() {
    this.setData({ shareVisible: true })
  },

  // 隐藏分享面板
  hideShare() {
    this.setData({ shareVisible: false })
  },

  // 复制邀请码
  copyCode() {
    wx.setClipboardData({
      data: this.data.code,
      success: () => {
        wx.showToast({
          title: '邀请码已复制',
          icon: 'success'
        })
      }
    })
  },

  // 生成分享文案
  generateShareText() {
    const text = `【约呗】我发起了一个聚会，邀请码：${this.data.code}，快来加入吧！`
    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({
          title: '文案已复制',
          icon: 'success'
        })
      }
    })
  },

  // 分享给朋友
  onShareAppMessage() {
    return {
      title: `邀请您加入聚会，邀请码：${this.data.code}`,
      path: `/pages/join/join?code=${this.data.code}`,
      imageUrl: '/assets/images/share.png'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: `约呗 - 聚会邀请码：${this.data.code}`,
      query: `code=${this.data.code}`
    }
  },

  // 返回首页
  goHome() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})