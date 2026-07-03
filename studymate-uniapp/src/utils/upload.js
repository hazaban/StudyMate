import { request } from '@/api/client.js'

/**
 * COS upload utility.
 *
 * Requests a POST Object signature from our backend, then uploads the file
 * directly to Tencent COS — no file data passes through the backend.
 */

/** @returns {Promise<{policy:string, signature:string, sessionToken:string, bucket:string, region:string, keyPrefix:string, expiredTime:number}>} */
async function fetchSignature(keyPrefix = '') {
  const params = keyPrefix ? `?key_prefix=${encodeURIComponent(keyPrefix)}` : ''
  return request(`/upload/signature${params}`, { method: 'POST' })
}

async function chooseImage(count = 1) {
  return new Promise((resolve, reject) => {
    uni.chooseImage({
      count,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => resolve(res.tempFilePaths),
      fail: (err) => reject(err),
    })
  })
}

async function compressImage(filePath) {
  return new Promise((resolve, reject) => {
    uni.compressImage({
      src: filePath,
      quality: 60,
      width: 1080,
      height: 1080,
      success: (res) => resolve(res.tempFilePath),
      fail: (err) => reject(err),
    })
  })
}

async function uploadToCOS(filePath, userId, date, keyPrefix = '') {
  try {
    const compressedPath = await compressImage(filePath)

    // Get signature + bucket/region from backend
    const sig = await fetchSignature(keyPrefix)

    const timestamp = Date.now()
    const filename = `${timestamp}.jpg`
    const key = `${sig.keyPrefix}${date ? date + '/' : ''}${filename}`

    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: `https://${sig.bucket}.cos.${sig.region}.myqcloud.com`,
        filePath: compressedPath,
        name: 'file',
        formData: {
          key,
          policy: sig.policy,
          signature: sig.signature,
          'x-cos-security-token': sig.sessionToken || '',
          'Content-Type': 'image/jpeg',
        },
        success: (res) => {
          if (res.statusCode === 204 || res.statusCode === 200) {
            const imageUrl = `https://${sig.bucket}.cos.${sig.region}.myqcloud.com/${key}`
            resolve(imageUrl)
          } else {
            reject(new Error(`上传失败 (${res.statusCode})`))
          }
        },
        fail: (err) => reject(err),
      })
    })
  } catch (error) {
    throw error
  }
}

export const uploadUtil = {
  chooseImage,
  compressImage,

  /** Upload a proof image to COS under proofs/{userId}/{date}/ */
  async uploadProof(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'proofs/')
  },

  /** Upload an avatar to COS under avatars/ */
  async uploadAvatar(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'avatars/')
  },

  /** Upload flash card question image to COS under cards/{userId}/{date}/question/ */
  async uploadCardQuestion(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'cards/question/')
  },

  /** Upload flash card answer image to COS under cards/{userId}/{date}/answer/ */
  async uploadCardAnswer(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'cards/answer/')
  },

  /** Upload mistake question image to COS under mistakes/{userId}/{date}/question/ */
  async uploadMistakeQuestion(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'mistakes/question/')
  },

  /** Upload mistake answer image to COS under mistakes/{userId}/{date}/answer/ */
  async uploadMistakeAnswer(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'mistakes/answer/')
  },

  /** Low-level: upload with full control over prefix and date */
  uploadToCOS,
}
