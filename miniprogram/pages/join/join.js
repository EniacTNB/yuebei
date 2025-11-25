// pages/join/join.js
const app = getApp()

Page({
  data: {
    code: '',
    gathering: null,
    nickname: '',
    myLocation: null,
    locationAddress: '',
    isJoining: false
  },

  onLoad(options) {
    if (options.code) {
      this.setData({ code: options.code })
      
      // 如果全局有聚会信息，直接使用
      if (app.globalData.currentGathering) {
        this.setData({ 
          gathering: app.globalData.currentGathering 
        })
      } else {
        // 否则重新获取
        this.loadGathering(options.code)
      }
    }
    
    // 获取当前位置
    this.getCurrentLocation()
  },

  // 加载聚会信息
  loadGathering(code) {
    wx.showLoading({ title: '加载中...' })
    
    wx.request({
      url: app.globalData.baseUrl + '/gathering/' + code,
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          this.setData({ gathering: res.data.data })
        } else {
          wx.showToast({
            title: '聚会不存在',
            icon: 'none'
          })
          setTimeout(() => {
            wx.navigateBack()
          }, 1500)
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    })
  },

  // 输入昵称
  inputNickname(e) {
    this.setData({
      nickname: e.detail.value
    })
  },

  // 获取当前位置
  getCurrentLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          myLocation: {
            lat: res.latitude,
            lng: res.longitude
          }
        })
        
        // 逆地理编码
        this.reverseGeocode(res.latitude, res.longitude)
      },
      fail: () => {
        // 位置获取失败，但不影响加入
        console.log('获取位置失败')
      }
    })
  },

  // 逆地理编码
  reverseGeocode(lat, lng) {
    wx.request({
      url: app.globalData.baseUrl + '/location/reverse-geocode',
      method: 'POST',
      data: { lat, lng },
      success: (res) => {
        if (res.data.success) {
          this.setData({
            locationAddress: res.data.data.formatted_address || res.data.data.address
          })
        }
      }
    })
  },

  // 选择位置
  chooseLocation() {
    wx.chooseLocation({
      success: (res) => {
        this.setData({
          myLocation: {
            lat: res.latitude,
            lng: res.longitude
          },
          locationAddress: res.address || res.name
        })
      }
    })
  },

  // 手动输入地址
  inputAddress() {
    wx.showModal({
      title: '输入地址',
      placeholderText: '请输入您的位置',
      editable: true,
      success: (res) => {
        if (res.confirm && res.content) {
          this.setData({
            locationAddress: res.content
          })
          
          // 地理编码
          this.geocodeAddress(res.content)
        }
      }
    })
  },

  // 地理编码
  geocodeAddress(address) {
    wx.request({
      url: app.globalData.baseUrl + '/location/geocode',
      method: 'POST',
      data: { address },
      success: (res) => {
        if (res.data.success) {
          this.setData({
            myLocation: res.data.data.location
          })
        }
      }
    })
  },

  // 加入聚会
  joinGathering() {
    if (!this.data.myLocation) {
      wx.showToast({
        title: '请先设置您的位置',
        icon: 'none'
      })
      return
    }
    
    if (this.data.isJoining) return
    
    this.setData({ isJoining: true })
    wx.showLoading({ title: '加入中...' })
    
    // 构建参与者信息
    const participant = {
      temp_id: app.globalData.userInfo.tempId,
      nickname: this.data.nickname || '匿名用户',
      location: {
        address: this.data.locationAddress,
        lat: this.data.myLocation.lat,
        lng: this.data.myLocation.lng
      },
      transport: 'driving' // 默认驾车，后续可以让用户选择
    }
    
    wx.request({
      url: app.globalData.baseUrl + '/gathering/join',
      method: 'POST',
      data: {
        code: this.data.code,
        participant: participant
      },
      success: (res) => {
        wx.hideLoading()
        
        if (res.data.success) {
          // 更新全局聚会信息
          app.globalData.currentGathering = res.data.data
          
          // 保存到历史
          this.saveToHistory(res.data.data)
          
          wx.showToast({
            title: '加入成功',
            icon: 'success'
          })
          
          // 跳转到结果页面
          setTimeout(() => {
            wx.redirectTo({
              url: '/pages/result/result?code=' + this.data.code
            })
          }, 1500)
        } else {
          wx.showToast({
            title: res.data.message || '加入失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ isJoining: false })
      }
    })
  },

  // 保存到历史记录
  saveToHistory(gathering) {
    try {
      let history = wx.getStorageSync('recent_gatherings') || []
      
      // 检查是否已存在
      const existIndex = history.findIndex(h => h.code === gathering.code)
      if (existIndex > -1) {
        // 更新现有记录
        history[existIndex] = {
          id: gathering.id,
          code: gathering.code,
          type: gathering.type,
          created_at: gathering.created_at,
          status: gathering.status,
          participants: gathering.participants || []
        }
      } else {
        // 添加新记录
        history.unshift({
          id: gathering.id,
          code: gathering.code,
          type: gathering.type,
          created_at: gathering.created_at,
          status: gathering.status,
          participants: gathering.participants || []
        })
      }
      
      // 只保留最近10个
      history = history.slice(0, 10)
      
      wx.setStorageSync('recent_gatherings', history)
    } catch (e) {
      console.error('保存历史记录失败', e)
    }
  }
})