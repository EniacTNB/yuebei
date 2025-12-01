// index.js
const app = getApp()

Page({
  data: {
    inviteCode: '',
    recentGatherings: [],
    showHelpModal: false,
    showRecentModal: false
  },

  onLoad() {
    // 加载最近的聚会（从本地缓存）
    this.loadRecentGatherings()
  },

  onShow() {
    // 页面显示时刷新数据
    this.loadRecentGatherings()
  },

  // 输入邀请码
  onCodeInput(e) {
    this.setData({
      inviteCode: e.detail.value.toUpperCase()
    })
  },

  // 发起新聚会
  handleCreate() {
    wx.navigateTo({
      url: '/pages/create/create'
    })
  },

  // 通过邀请码加入
  handleJoinByCode() {
    const { inviteCode } = this.data
    
    if (!inviteCode || inviteCode.length !== 6) {
      wx.showToast({
        title: '请输入6位邀请码',
        icon: 'none'
      })
      return
    }

    // 先验证邀请码是否有效
    wx.showLoading({ title: '验证中...' })
    
    wx.request({
      url: app.globalData.baseUrl + '/gathering/' + inviteCode,
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          // 保存到全局
          app.globalData.currentGathering = res.data.data
          // 跳转到加入页面
          wx.navigateTo({
            url: '/pages/join/join?code=' + inviteCode
          })
        } else {
          wx.showToast({
            title: res.data.message || '邀请码无效',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 重新加入最近的聚会
  handleRejoin(e) {
    const { id } = e.currentTarget.dataset
    const gathering = this.data.recentGatherings.find(g => g.id === id)

    if (gathering && gathering.code) {
      // 关闭弹窗
      this.closeRecentModal()
      // 跳转到结果页面
      wx.navigateTo({
        url: '/pages/result/result?code=' + gathering.code
      })
    }
  },

  // 加载最近的聚会
  loadRecentGatherings() {
    try {
      const gatherings = wx.getStorageSync('recent_gatherings') || []
      
      // 处理显示数据
      const processed = gatherings.map(g => {
        return {
          ...g,
          typeText: this.getTypeText(g.type),
          timeText: this.formatTime(g.created_at),
          statusText: this.getStatusText(g.status),
          memberCount: g.participants ? g.participants.length : 0
        }
      })
      
      this.setData({
        recentGatherings: processed.slice(0, 5) // 只显示最近5个
      })
    } catch (e) {
      console.error('加载历史记录失败', e)
    }
  },

  // 获取类型文本
  getTypeText(type) {
    const typeMap = {
      'meal': '吃饭',
      'coffee': '咖啡',
      'movie': '电影',
      'ktv': 'K歌',
      'other': '其他'
    }
    return typeMap[type] || '聚会'
  },

  // 格式化时间
  formatTime(timeStr) {
    if (!timeStr) return ''
    
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now - date
    
    if (diff < 3600000) {
      return Math.floor(diff / 60000) + '分钟前'
    } else if (diff < 86400000) {
      return Math.floor(diff / 3600000) + '小时前'
    } else {
      return Math.floor(diff / 86400000) + '天前'
    }
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'active': '进行中',
      'expired': '已过期',
      'cancelled': '已取消'
    }
    return statusMap[status] || '未知'
  },

  // 打开最近聚会弹窗
  openRecentModal() {
    this.setData({
      showRecentModal: true
    })
  },

  // 关闭最近聚会弹窗
  closeRecentModal() {
    this.setData({
      showRecentModal: false
    })
  },

  // 打开使用说明弹窗
  openHelpModal() {
    this.setData({
      showHelpModal: true
    })
  },

  // 关闭使用说明弹窗
  closeHelpModal() {
    this.setData({
      showHelpModal: false
    })
  },

  // 阻止遮罩下的页面滚动
  preventTouchMove() {
    return false
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '约呗 - 找到最方便的聚会地点',
      path: '/pages/index/index',
      imageUrl: '/assets/images/share.png'
    }
  }
})