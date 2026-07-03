const COS_BUCKET = process.env.VUE_APP_COS_BUCKET
const COS_REGION = process.env.VUE_APP_COS_REGION

export const uploadUtil = {
  async chooseImage(count = 1) {
    return new Promise((resolve, reject) => {
      uni.chooseImage({
        count,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          resolve(res.tempFilePaths)
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  async compressImage(filePath) {
    return new Promise((resolve, reject) => {
      uni.compressImage({
        src: filePath,
        quality: 60,
        width: 1080,
        height: 1080,
        success: (res) => {
          resolve(res.tempFilePath)
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  async getUploadSignature() {
    const response = await uni.request({
      url: process.env.VUE_APP_SIGNATURE_URL,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      }
    })

    if (response.statusCode !== 200) {
      throw new Error('获取签名失败')
    }

    return response.data
  },

  async uploadToCOS(filePath, userId, date) {
    try {
      const compressedPath = await this.compressImage(filePath)
      const signature = await this.getUploadSignature()

      const timestamp = Date.now()
      const filename = `${timestamp}.jpg`
      const key = `proofs/${userId}/${date}/${filename}`

      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: `https://${COS_BUCKET}.cos.${COS_REGION}.myqcloud.com`,
          filePath: compressedPath,
          name: 'file',
          formData: {
            key,
            policy: signature.policy,
            signature: signature.signature,
            'x-cos-security-token': signature.sessionToken,
            'Content-Type': 'image/jpeg'
          },
          success: (res) => {
            if (res.statusCode === 204) {
              const imageUrl = `https://${COS_BUCKET}.cos.${COS_REGION}.myqcloud.com/${key}`
              resolve(imageUrl)
            } else {
              reject(new Error('上传失败'))
            }
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    } catch (error) {
      throw error
    }
  },

  async uploadProof(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return this.uploadToCOS(imagePath, userId, today)
  },

  async uploadAvatar(imagePath, userId) {
    const filename = `${userId}.jpg`
    const key = `avatars/${filename}`

    try {
      const compressedPath = await this.compressImage(imagePath)
      const signature = await this.getUploadSignature()

      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: `https://${COS_BUCKET}.cos.${COS_REGION}.myqcloud.com`,
          filePath: compressedPath,
          name: 'file',
          formData: {
            key,
            policy: signature.policy,
            signature: signature.signature,
            'x-cos-security-token': signature.sessionToken,
            'Content-Type': 'image/jpeg'
          },
          success: (res) => {
            if (res.statusCode === 204) {
              const imageUrl = `https://${COS_BUCKET}.cos.${COS_REGION}.myqcloud.com/${key}`
              resolve(imageUrl)
            } else {
              reject(new Error('上传失败'))
            }
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    } catch (error) {
      throw error
    }
  }
}