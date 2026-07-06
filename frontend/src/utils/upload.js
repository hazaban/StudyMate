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
  // H5端用Canvas压缩，避免上传原图太大
  try {
    let blob
    if (blobUrlToFile.has(filePath)) {
      blob = blobUrlToFile.get(filePath)
    } else if (filePath.startsWith('blob:')) {
      const res = await fetch(filePath)
      blob = await res.blob()
    } else {
      return filePath
    }
    // 小于200KB的图片不压缩
    if (blob.size < 200 * 1024) {
      return filePath
    }
    const compressedBlob = await compressBlobWithCanvas(blob, 1920, 0.85)
    // 用压缩后的blob替换原blob
    blobUrlToFile.set(filePath, compressedBlob)
    return filePath
  } catch (e) {
    return filePath
  }
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

// #ifdef H5
function compressBlobWithCanvas(blob, maxSize, quality) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(blob)
    img.onload = () => {
      let { width, height } = img
      // 等比缩放到maxSize以内
      if (width > maxSize || height > maxSize) {
        if (width > height) {
          height = Math.round(height * maxSize / width)
          width = maxSize
        } else {
          width = Math.round(width * maxSize / height)
          height = maxSize
        }
      }
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)
      canvas.toBlob(
        (compressedBlob) => {
          URL.revokeObjectURL(url)
          if (compressedBlob && compressedBlob.size < blob.size) {
            resolve(compressedBlob)
          } else {
            resolve(blob)
          }
        },
        'image/jpeg',
        quality
      )
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(blob)
    }
    img.src = url
  })
}
// #endif

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
  // 上传前先压缩图片
  await compressImage(filePath)
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
