// pages/create/create.js
const app = getApp()

Page({
  data: {
    types: [
      { value: 'meal', text: '🍜 吃饭', checked: true },
      { value: 'coffee', text: '☕ 咖啡', checked: false },
      { value: 'movie', text: '🎬 电影', checked: false },
      { value: 'ktv', text: '🎤 K歌', checked: false },
      { value: 'other', text: '🎉 其他', checked: false }
    ],
    selectedType: 'meal',
    myLocation: null,
    locationAddress: '',
    isCreating: false
  },

  onLoad() {
    // 获取当前位置
    this.getCurrentLocation()
  },

  // 选择类型
  selectType(e) {
    const { value } = e.currentTarget.dataset
    const types = this.data.types.map(t => ({
      ...t,
      checked: t.value === value
    }))
    
    this.setData({
      types,
      selectedType: value
    })
  },

  // 获取当前位置
  getCurrentLocation() {
    wx.showLoading({ title: '获取位置中...' })
    
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        wx.hideLoading()
        
        this.setData({
          myLocation: {
            lat: res.latitude,
            lng: res.longitude
          }
        })
        
        // 逆地理编码获取地址
        this.reverseGeocode(res.latitude, res.longitude)
      },
      fail: (err) => {
        wx.hideLoading()
        
        if (err.errMsg.includes('auth deny')) {
          // 用户拒绝授权
          wx.showModal({
            title: '需要位置权限',
            content: '请允许获取位置信息，以便推荐最佳聚会地点',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                wx.openSetting()
              }
            }
          })
        } else {
          wx.showToast({
            title: '获取位置失败',
            icon: 'none'
          })
        }
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

  // 创建聚会
  createGathering() {
    if (this.data.isCreating) return
    
    this.setData({ isCreating: true })
    wx.showLoading({ title: '创建中...' })
    
    const requestData = {
      type: this.data.selectedType,
      preferences: {}
    }
    
    // 如果有位置信息，添加创建者位置
    if (this.data.myLocation) {
      requestData.creator_location = {
        address: this.data.locationAddress,
        lat: this.data.myLocation.lat,
        lng: this.data.myLocation.lng
      }
    }
    
    wx.request({
      url: app.globalData.baseUrl + '/gathering/create',
      method: 'POST',
      data: requestData,
      success: (res) => {
        wx.hideLoading()
        
        if (res.data.success) {
          const gathering = res.data.data
          
          // 保存到全局
          app.globalData.currentGathering = gathering
          
          // 保存到本地历史
          this.saveToHistory(gathering)
          
          // 显示成功
          wx.showToast({
            title: '创建成功',
            icon: 'success'
          })
          
          // 延迟跳转到结果页面
          setTimeout(() => {
            wx.redirectTo({
              url: '/pages/result/result?code=' + gathering.code + '&isCreator=true'
            })
          }, 1500)
        } else {
          wx.showToast({
            title: res.data.message || '创建失败',
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
        this.setData({ isCreating: false })
      }
    })
  },

  // 保存到历史记录
  saveToHistory(gathering) {
    try {
      let history = wx.getStorageSync('recent_gatherings') || []
      
      // 添加到开头
      history.unshift({
        id: gathering.id,
        code: gathering.code,
        type: gathering.type,
        created_at: gathering.created_at,
        status: gathering.status,
        participants: gathering.participants || []
      })
      
      // 只保留最近10个
      history = history.slice(0, 10)
      
      wx.setStorageSync('recent_gatherings', history)
    } catch (e) {
      console.error('保存历史记录失败', e)
    }
  }
})