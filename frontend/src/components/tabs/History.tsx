import { useState, useEffect } from 'react'
import { Box, VStack, Text, HStack, Button } from '@chakra-ui/react'
import axios from '../../lib/axios'

interface HistoryEntry {
  id: string
  timestamp: string
  type: 'execution' | 'file_change' | 'workspace_change'
  description: string
  details?: string
}

function History() {
  const [history, setHistory] = useState<HistoryEntry[]>([])

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response = await axios.get('/api/history/')
      setHistory(response.data.history)
    } catch (error) {
      console.error('Error loading history:', error)
      // Fallback to localStorage
      const savedHistory = localStorage.getItem('ide_history')
      if (savedHistory) {
        setHistory(JSON.parse(savedHistory))
      }
    }
  }


  const clearHistory = async () => {
    if (confirm('Clear all history?')) {
      try {
        await axios.delete('/api/history/')
        setHistory([])
        localStorage.removeItem('ide_history')
      } catch (error) {
        console.error('Error clearing history:', error)
        // Fallback to localStorage
        setHistory([])
        localStorage.removeItem('ide_history')
      }
    }
  }

  const getTypeIcon = (type: HistoryEntry['type']) => {
    switch (type) {
      case 'execution':
        return '▶️'
      case 'file_change':
        return '📝'
      case 'workspace_change':
        return '🔧'
      default:
        return '📌'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  return (
    <Box h="100%">
      <VStack align="stretch" gap={4} h="100%">
        <HStack justify="space-between">
          <Text fontSize="lg" color="midnight.400" fontWeight="bold">
            History & Activity
          </Text>
          <Button size="sm" variant="ghost" onClick={clearHistory}>
            🗑 Clear History
          </Button>
        </HStack>

        {history.length === 0 ? (
          <VStack h="100%" justify="center" gap={4}>
            <Text fontSize="lg" color="midnight.400">
              No history yet
            </Text>
            <Text fontSize="sm" color="midnight.500" textAlign="center">
              Your code executions, file changes, and workspace modifications
              <br />
              will appear here
            </Text>
          </VStack>
        ) : (
          <VStack align="stretch" gap={2} overflowY="auto">
            {history.map((entry) => (
              <Box
                key={entry.id}
                p={4}
                bg="rgba(27, 16, 42, 0.5)"
                border="1px solid"
                borderColor="midnight.700"
                borderRadius="md"
                _hover={{ borderColor: 'purple.500' }}
              >
                <HStack justify="space-between" mb={2}>
                  <HStack>
                    <Text fontSize="lg">{getTypeIcon(entry.type)}</Text>
                    <Text fontSize="sm" color="midnight.400" fontWeight="bold">
                      {entry.description}
                    </Text>
                  </HStack>
                  <Text fontSize="xs" color="midnight.500">
                    {formatTimestamp(entry.timestamp)}
                  </Text>
                </HStack>
                {entry.details && (
                  <Text fontSize="xs" color="midnight.500" fontFamily="monospace" mt={2}>
                    {entry.details}
                  </Text>
                )}
              </Box>
            ))}
          </VStack>
        )}

        <Box
          p={4}
          bg="rgba(27, 16, 42, 0.5)"
          border="1px solid"
          borderColor="midnight.700"
          borderRadius="md"
        >
          <Text fontSize="sm" color="midnight.400" fontWeight="bold" mb={2}>
            Statistics
          </Text>
          <HStack gap={6}>
            <Box>
              <Text fontSize="xs" color="midnight.500">Total Entries</Text>
              <Text fontSize="lg" color="midnight.400" fontWeight="bold">
                {history.length}
              </Text>
            </Box>
            <Box>
              <Text fontSize="xs" color="midnight.500">Executions</Text>
              <Text fontSize="lg" color="midnight.400" fontWeight="bold">
                {history.filter(h => h.type === 'execution').length}
              </Text>
            </Box>
            <Box>
              <Text fontSize="xs" color="midnight.500">File Changes</Text>
              <Text fontSize="lg" color="midnight.400" fontWeight="bold">
                {history.filter(h => h.type === 'file_change').length}
              </Text>
            </Box>
          </HStack>
        </Box>
      </VStack>
    </Box>
  )
}

export default History
