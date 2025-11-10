import { useState } from 'react'
import { Box, Text, HStack, Button } from '@chakra-ui/react'
import axios from '../lib/axios'

interface FileNode {
  name: string
  path: string
  type: 'file' | 'folder'
  extension?: string
  children?: FileNode[]
}

interface FileTreeProps {
  onFileSelect: (path: string) => void
  selectedFile?: string
  isCollapsed?: boolean
}

function FileTree({ onFileSelect, selectedFile, isCollapsed }: FileTreeProps) {
  const [tree, setTree] = useState<FileNode[]>([])
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [draggedItem, setDraggedItem] = useState<string | null>(null)
  const [dragOverFolder, setDragOverFolder] = useState<string | null>(null)

  const loadTree = async () => {
    try {
      const response = await axios.get('/api/files/tree')
      setTree(response.data.tree)
    } catch (error) {
      console.error('Error loading file tree:', error)
    }
  }

  useState(() => {
    loadTree()
  })

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedFolders(newExpanded)
  }

  const deleteItem = async (path: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm(`Delete ${path}?`)) return
    
    try {
      await axios.delete(`/api/files/${path}`)
      await loadTree()
      console.log('Deleted successfully')
    } catch (error) {
      console.error('Error deleting:', error)
    }
  }

  const handleDragStart = (path: string, e: React.DragEvent) => {
    e.stopPropagation()
    setDraggedItem(path)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragOver = (path: string, isFolder: boolean, e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (isFolder && draggedItem && draggedItem !== path) {
      setDragOverFolder(path)
      e.dataTransfer.dropEffect = 'move'
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.stopPropagation()
    setDragOverFolder(null)
  }

  const handleDrop = async (targetFolderPath: string, e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!draggedItem || draggedItem === targetFolderPath) {
      setDragOverFolder(null)
      setDraggedItem(null)
      return
    }

    // Prevent moving a folder into itself or its descendants
    if (targetFolderPath.startsWith(draggedItem + '/')) {
      alert('Cannot move a folder into itself or its subdirectories')
      setDragOverFolder(null)
      setDraggedItem(null)
      return
    }

    // Prevent no-op moves (moving to current parent)
    const draggedParent = draggedItem.substring(0, draggedItem.lastIndexOf('/'))
    if (draggedParent === targetFolderPath) {
      setDragOverFolder(null)
      setDraggedItem(null)
      return
    }

    try {
      await axios.post('/api/files/move', {
        source: draggedItem,
        target_folder: targetFolderPath
      })
      await loadTree()
      console.log('Moved successfully')
    } catch (error) {
      console.error('Error moving file:', error)
      alert('Error moving file')
    } finally {
      setDragOverFolder(null)
      setDraggedItem(null)
    }
  }

  const renderNode = (node: FileNode, level: number = 0) => {
    const isExpanded = expandedFolders.has(node.path)
    const isSelected = selectedFile === node.path
    const isDraggedOver = dragOverFolder === node.path
    const isDragging = draggedItem === node.path

    if (node.type === 'folder') {
      return (
        <Box key={node.path} ml={level * 4}>
          <HStack
            p={1}
            px={2}
            cursor="pointer"
            bg={isDraggedOver ? 'midnight.600' : isSelected ? 'midnight.700' : 'transparent'}
            _hover={{ bg: 'midnight.700', opacity: 0.8 }}
            borderRadius="md"
            onClick={() => toggleFolder(node.path)}
            draggable
            onDragStart={(e) => handleDragStart(node.path, e)}
            onDragOver={(e) => handleDragOver(node.path, true, e)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(node.path, e)}
            opacity={isDragging ? 0.5 : 1}
            border={isDraggedOver ? '2px dashed' : 'none'}
            borderColor="midnight.500"
          >
            <Text fontSize="sm" color="midnight.400">{isExpanded ? '▾' : '▸'}</Text>
            <Text flex="1" fontSize="sm" color="midnight.300">{node.name}</Text>
            <Button
              size="xs"
              variant="ghost"
              onClick={(e) => deleteItem(node.path, e)}
              p={0}
              minW="auto"
              color="midnight.400"
              _hover={{ color: 'red.400' }}
            >
              ×
            </Button>
          </HStack>
          {isExpanded && node.children && (
            <Box>
              {node.children.map(child => renderNode(child, level + 1))}
            </Box>
          )}
        </Box>
      )
    }

    const getFileIcon = (ext?: string) => {
      if (!ext) return '•'
      const extensions: Record<string, string> = {
        '.py': 'py',
        '.js': 'js',
        '.jsx': 'jsx',
        '.ts': 'ts',
        '.tsx': 'tsx',
        '.json': 'json',
        '.md': 'md',
        '.ipynb': 'ipynb',
        '.html': 'html',
        '.css': 'css',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.h': 'h',
        '.hpp': 'hpp',
        '.cs': 'cs',
        '.php': 'php',
        '.csv': 'csv',
        '.xlsx': 'xlsx',
        '.xls': 'xls',
        '.txt': 'txt',
        '.png': 'png',
        '.jpg': 'jpg',
        '.jpeg': 'jpg',
        '.gif': 'gif',
        '.svg': 'svg',
        '.webp': 'webp',
        '.pdf': 'pdf',
        '.zip': 'zip',
        '.tar': 'tar',
        '.gz': 'gz',
        '.xml': 'xml',
        '.yml': 'yml',
        '.yaml': 'yaml',
        '.sql': 'sql',
        '.sh': 'sh',
        '.bash': 'bash',
        '.java': 'java',
        '.rb': 'rb',
        '.go': 'go',
        '.rs': 'rs',
        '.swift': 'swift',
        '.kt': 'kt',
        '.kts': 'kt'
      }
      return extensions[ext] || '•'
    }

    return (
      <HStack
        key={node.path}
        ml={level * 4}
        p={1}
        px={2}
        cursor="pointer"
        bg={isSelected ? 'midnight.700' : 'transparent'}
        _hover={{ bg: 'midnight.700', opacity: 0.8 }}
        borderRadius="md"
        onClick={() => onFileSelect(node.path)}
        draggable
        onDragStart={(e) => handleDragStart(node.path, e)}
        opacity={isDragging ? 0.5 : 1}
      >
        <Text 
          fontSize="xs" 
          color="midnight.500" 
          fontFamily="monospace"
          minW="40px"
          textAlign="left"
        >
          {getFileIcon(node.extension)}
        </Text>
        <Text flex="1" fontSize="sm" color="midnight.400">{node.name}</Text>
        <Button
          size="xs"
          variant="ghost"
          onClick={(e) => deleteItem(node.path, e)}
          p={0}
          minW="auto"
          color="midnight.400"
          _hover={{ color: 'red.400' }}
        >
          ×
        </Button>
      </HStack>
    )
  }

  if (isCollapsed) {
    return null
  }

  return (
    <Box>
      {tree.map(node => renderNode(node))}
      {tree.length === 0 && (
        <Text fontSize="sm" color="midnight.500" textAlign="center" p={4}>
          No files yet
        </Text>
      )}
    </Box>
  )
}

export default FileTree
