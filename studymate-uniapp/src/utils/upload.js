import { request } from '@/api/client.js'

const blobUrlToFile = new Map()

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
  // #ifdef H5
  return filePath
  // #endif
  // #ifndef H5
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
  // #endif
}

async function blobUrlToBlob(blobUrl) {
  if (blobUrlToFile.has(blobUrl)) {
    return blobUrlToFile.get(blobUrl)
  }
  const res = await fetch(blobUrl)
  return res.blob()
}

async function uploadToCOS(filePath, userId, date, keyPrefix = '') {
  const sig = await fetchSignature(keyPrefix)

  const timestamp = Date.now()
  const filename = `${timestamp}.jpg`
  const key = `${sig.keyPrefix}${date ? date + '/' : ''}${filename}`
  const imageUrl = `https://${sig.bucket}.cos.${sig.region}.myqcloud.com/${key}`

  const formData = {
    key,
    policy: sig.policy,
    signature: sig.signature,
    'x-cos-security-token': sig.sessionToken || '',
    'Content-Type': 'image/jpeg',
  }

  // #ifdef H5
  let fileBlob
  if (blobUrlToFile.has(filePath)) {
    fileBlob = blobUrlToFile.get(filePath)
  } else if (filePath.startsWith('blob:')) {
    fileBlob = await blobUrlToBlob(filePath)
  } else {
    fileBlob = await blobUrlToBlob(filePath)
  }

  const fd = new FormData()
  Object.keys(formData).forEach(k => fd.append(k, formData[k]))
  fd.append('file', fileBlob, filename)

  const res = await fetch(`https://${sig.bucket}.cos.${sig.region}.myqcloud.com`, {
    method: 'POST',
    body: fd,
  })

  if (res.status === 204 || res.status === 200) {
    return imageUrl
  } else {
    throw new Error(`上传失败 (${res.status})`)
  }
  // #endif

  // #ifndef H5
  const compressedPath = await compressImage(filePath)
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `https://${sig.bucket}.cos.${sig.region}.myqcloud.com`,
      filePath: compressedPath,
      name: 'file',
      formData,
      success: (res) => {
        if (res.statusCode === 204 || res.statusCode === 200) {
          resolve(imageUrl)
        } else {
          reject(new Error(`上传失败 (${res.statusCode})`))
        }
      },
      fail: (err) => reject(err),
    })
  })
  // #endif
}

export const uploadUtil = {
  chooseImage,
  compressImage,

  async pasteToFiles(event) {
    // #ifdef H5
    const items = event.clipboardData?.items
    if (!items) return []
    const files = []
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (file) {
          const url = URL.createObjectURL(file)
          blobUrlToFile.set(url, file)
          files.push(url)
        }
      }
    }
    return files
    // #endif
    // #ifndef H5
    return []
    // #endif
  },

  async uploadProof(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'proofs/')
  },

  async uploadAvatar(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'avatars/')
  },

  async uploadCardQuestion(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'cards/question/')
  },

  async uploadCardAnswer(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'cards/answer/')
  },

  async uploadMistakeQuestion(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'mistakes/question/')
  },

  async uploadMistakeAnswer(imagePath, userId) {
    const today = new Date().toISOString().split('T')[0]
    return uploadToCOS(imagePath, userId, today, 'mistakes/answer/')
  },

  uploadToCOS,
}
