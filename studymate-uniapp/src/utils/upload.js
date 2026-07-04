import { request } from '@/api/client.js'

const blobUrlToFile = new Map()

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
  // Get presigned PUT URL from backend
  const result = await request(`/upload/presign?filename=${Date.now()}.jpg`, {
    method: 'POST'
  })
  const { upload_url, file_url } = result

  // #ifdef H5
  let fileBlob
  if (blobUrlToFile.has(filePath)) {
    fileBlob = blobUrlToFile.get(filePath)
  } else if (filePath.startsWith('blob:')) {
    fileBlob = await blobUrlToBlob(filePath)
  } else {
    fileBlob = await blobUrlToBlob(filePath)
  }

  const res = await fetch(upload_url, {
    method: 'PUT',
    body: fileBlob,
  })

  if (res.status === 200) {
    return file_url
  } else {
    throw new Error(`上传失败 (${res.status})`)
  }
  // #endif

  // #ifndef H5
  const compressedPath = await compressImage(filePath)
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: upload_url,
      filePath: compressedPath,
      name: 'file',
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(file_url)
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
    return uploadToCOS(imagePath, userId, '', 'proofs/')
  },

  async uploadAvatar(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'avatars/')
  },

  async uploadCardQuestion(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'cards/question/')
  },

  async uploadCardAnswer(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'cards/answer/')
  },

  async uploadMistakeQuestion(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'mistakes/question/')
  },

  async uploadMistakeAnswer(imagePath, userId) {
    return uploadToCOS(imagePath, userId, '', 'mistakes/answer/')
  },

  uploadToCOS,
}
