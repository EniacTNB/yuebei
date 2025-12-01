// pages/result/result.js
const app = getApp()

Page({
  data: {
    code: '',
    isCreator: false,
    gathering: null,
    recommendations: [],
    isLoading: true,
    shareVisible: false,
    isSinglePerson: false,  // 是否只有一个人
    nearbyPlaces: [],       // 附近地点（单人模式）

    // 添加参与者相关
    showAddParticipantModal: false,
    newParticipant: {
      nickname: '',
      location: null,
      transport_mode: 'driving'
    },

    // 添加地点相关
    showAddPlaceModal: false,
    newPlace: {
      name: '',
      address: '',
      location: null,
      rating: null
    }
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
          const gathering = res.data.data
          const participantCount = gathering.participants ? gathering.participants.length : 0

          this.setData({
            gathering: gathering,
            isSinglePerson: participantCount === 1
          })

          // 如果只有一个人，加载附近地点
          if (participantCount === 1) {
            this.loadNearbyPlaces(gathering)
          }
        }
      }
    })
  },

  // 加载推荐结果
  loadRecommendations(code) {
    // 如果只有一个人，不加载推荐
    if (this.data.isSinglePerson) {
      this.setData({ isLoading: false })
      return
    }

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

  // 加载附近地点（单人模式）
  loadNearbyPlaces(gathering) {
    if (!gathering.participants || gathering.participants.length === 0) {
      return
    }

    const firstPerson = gathering.participants[0]
    if (!firstPerson.location) {
      return
    }

    this.setData({ isLoading: true })

    // 调用后端 API 搜索附近地点
    wx.request({
      url: app.globalData.baseUrl + '/location/search',
      method: 'GET',
      data: {
        keyword: this.getTypeKeyword(gathering.type),
        lat: firstPerson.location.lat,
        lng: firstPerson.location.lng,
        radius: 2000  // 搜索半径2公里
      },
      success: (res) => {
        if (res.data.success) {
          this.setData({
            nearbyPlaces: res.data.data || [],
            isLoading: false
          })
        } else {
          // 失败时使用模拟数据
          this.loadMockNearbyPlaces(gathering.type)
        }
      },
      fail: () => {
        // 失败时使用模拟数据
        this.loadMockNearbyPlaces(gathering.type)
      }
    })
  },

  // 根据聚会类型获取搜索关键词
  getTypeKeyword(type) {
    const typeMap = {
      'meal': '餐厅',
      'coffee': '咖啡厅',
      'movie': '电影院',
      'ktv': 'KTV',
      'other': '休闲娱乐'
    }
    return typeMap[type] || '美食'
  },

  // 加载模拟附近地点
  loadMockNearbyPlaces(type) {
    const mockPlaces = [
      {
        id: 1,
        name: '星巴克咖啡',
        address: '附近500米',
        distance: 500,
        rating: 4.5,
        type: type
      },
      {
        id: 2,
        name: '肯德基餐厅',
        address: '附近800米',
        distance: 800,
        rating: 4.2,
        type: type
      },
      {
        id: 3,
        name: '海底捞火锅',
        address: '附近1.2公里',
        distance: 1200,
        rating: 4.8,
        type: type
      }
    ]

    this.setData({
      nearbyPlaces: mockPlaces,
      isLoading: false
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

  // 查看附近地点详情
  viewNearbyDetail(e) {
    const { index } = e.currentTarget.dataset
    const place = this.data.nearbyPlaces[index]

    wx.showModal({
      title: place.name,
      content: `地址：${place.address}\n${place.distance ? '距离：' + place.distance + '米' : ''}\n${place.rating ? '评分：' + place.rating + '分' : ''}`,
      confirmText: '导航',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm && place.location) {
          this.navigateToPlace(place)
        }
      }
    })
  },

  // 导航到地点（通用方法）
  navigateToPlace(place) {
    if (!place.location) {
      wx.showToast({
        title: '暂无位置信息',
        icon: 'none'
      })
      return
    }

    wx.openLocation({
      latitude: place.location.lat,
      longitude: place.location.lng,
      name: place.name,
      address: place.address || '',
      scale: 18
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
  },

  // ==================== 参与者管理 ====================

  // 显示添加参与者弹窗
  showAddParticipant() {
    this.setData({
      showAddParticipantModal: true,
      newParticipant: {
        nickname: '',
        location: null,
        transport_mode: 'driving'
      }
    })
  },

  // 隐藏添加参与者弹窗
  hideAddParticipant() {
    this.setData({ showAddParticipantModal: false })
  },

  // 输入昵称
  onParticipantNicknameInput(e) {
    this.setData({
      'newParticipant.nickname': e.detail.value
    })
  },

  // 选择参与者位置
  chooseParticipantLocation() {
    wx.chooseLocation({
      success: (res) => {
        this.setData({
          'newParticipant.location': {
            lat: res.latitude,
            lng: res.longitude,
            address: res.address || res.name
          }
        })
      },
      fail: (err) => {
        if (err.errMsg.indexOf('auth deny') !== -1) {
          wx.showModal({
            title: '需要位置权限',
            content: '请在设置中开启位置权限',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                wx.openSetting()
              }
            }
          })
        }
      }
    })
  },

  // 选择交通方式
  selectTransport(e) {
    const { mode } = e.currentTarget.dataset
    this.setData({
      'newParticipant.transport_mode': mode
    })
  },

  // 确认添加参与者
  confirmAddParticipant() {
    const { newParticipant } = this.data

    // 验证
    if (!newParticipant.nickname) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }

    if (!newParticipant.location) {
      wx.showToast({
        title: '请选择位置',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '添加中...' })

    // 调用后端API添加参与者
    wx.request({
      url: app.globalData.baseUrl + '/gathering/join',
      method: 'POST',
      data: {
        code: this.data.code,
        participant: {
          temp_id: 'user_' + Date.now(),
          nickname: newParticipant.nickname,
          location: newParticipant.location,
          transport_mode: newParticipant.transport_mode
        }
      },
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          wx.showToast({
            title: '添加成功',
            icon: 'success'
          })

          // 隐藏弹窗
          this.hideAddParticipant()

          // 重新加载数据
          this.loadGathering(this.data.code)
          this.loadRecommendations(this.data.code)
        } else {
          wx.showToast({
            title: res.data.message || '添加失败',
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
      }
    })
  },

  // 删除参与者
  deleteParticipant(e) {
    const { id } = e.currentTarget.dataset

    wx.showModal({
      title: '确认删除',
      content: '确定要移除该参与者吗？',
      success: (res) => {
        if (res.confirm) {
          this.performDeleteParticipant(id)
        }
      }
    })
  },

  // 执行删除参与者
  performDeleteParticipant(tempId) {
    wx.showLoading({ title: '删除中...' })

    // 调用后端API删除参与者
    wx.request({
      url: app.globalData.baseUrl + '/gathering/' + this.data.code + '/participant/' + tempId,
      method: 'DELETE',
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })

          // 重新加载数据
          this.loadGathering(this.data.code)
          this.loadRecommendations(this.data.code)
        } else {
          wx.showToast({
            title: res.data.message || '删除失败',
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
      }
    })
  },

  // ==================== 地点管理 ====================

  // 显示添加地点弹窗
  showAddPlace() {
    this.setData({
      showAddPlaceModal: true,
      newPlace: {
        name: '',
        address: '',
        location: null,
        rating: null
      }
    })
  },

  // 隐藏添加地点弹窗
  hideAddPlace() {
    this.setData({ showAddPlaceModal: false })
  },

  // 输入地点名称
  onPlaceNameInput(e) {
    this.setData({
      'newPlace.name': e.detail.value
    })
  },

  // 输入地点评分
  onPlaceRatingInput(e) {
    const rating = parseFloat(e.detail.value)
    if (rating >= 1 && rating <= 5) {
      this.setData({
        'newPlace.rating': rating
      })
    }
  },

  // 选择地点位置
  choosePlaceLocation() {
    wx.chooseLocation({
      success: (res) => {
        this.setData({
          'newPlace.address': res.address || res.name,
          'newPlace.location': {
            lat: res.latitude,
            lng: res.longitude
          },
          'newPlace.name': this.data.newPlace.name || res.name
        })
      },
      fail: (err) => {
        if (err.errMsg.indexOf('auth deny') !== -1) {
          wx.showModal({
            title: '需要位置权限',
            content: '请在设置中开启位置权限',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                wx.openSetting()
              }
            }
          })
        }
      }
    })
  },

  // 确认添加地点
  confirmAddPlace() {
    const { newPlace } = this.data

    // 验证
    if (!newPlace.name) {
      wx.showToast({
        title: '请输入地点名称',
        icon: 'none'
      })
      return
    }

    if (!newPlace.location) {
      wx.showToast({
        title: '请选择位置',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '添加中...' })

    // 调用后端API添加地点
    wx.request({
      url: app.globalData.baseUrl + '/gathering/' + this.data.code + '/place',
      method: 'POST',
      data: {
        name: newPlace.name,
        address: newPlace.address,
        location: newPlace.location,
        rating: newPlace.rating
      },
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          wx.showToast({
            title: '添加成功',
            icon: 'success'
          })

          // 隐藏弹窗
          this.hideAddPlace()

          // 重新加载推荐
          this.loadRecommendations(this.data.code)
        } else {
          wx.showToast({
            title: res.data.message || '添加失败',
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
      }
    })
  },

  // 删除地点
  deletePlace(e) {
    const { id } = e.currentTarget.dataset

    wx.showModal({
      title: '确认删除',
      content: '确定要删除该候选地点吗？',
      success: (res) => {
        if (res.confirm) {
          this.performDeletePlace(id)
        }
      }
    })
  },

  // 执行删除地点
  performDeletePlace(placeId) {
    wx.showLoading({ title: '删除中...' })

    // 调用后端API删除地点
    wx.request({
      url: app.globalData.baseUrl + '/gathering/' + this.data.code + '/place/' + placeId,
      method: 'DELETE',
      success: (res) => {
        wx.hideLoading()
        if (res.data.success) {
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })

          // 重新加载推荐
          this.loadRecommendations(this.data.code)
        } else {
          wx.showToast({
            title: res.data.message || '删除失败',
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
      }
    })
  },

  // 防止穿透
  preventTouchMove() {
    return false
  }
})