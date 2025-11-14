import { Box, Flex, Text } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import MainContent from './components/MainContent'
import LandingPage from './pages/LandingPage'
import UserMenu from './components/UserMenu'

function App() {
  const [selectedFile, setSelectedFile] = useState<string | undefined>()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    // Check for auth token or guest mode
    const token = localStorage.getItem('auth_token')
    const guestMode = localStorage.getItem('guest_mode')
    
    if (token || guestMode === 'true') {
      setIsAuthenticated(true)
    } else {
      setIsAuthenticated(false)
    }

    // Check for OAuth callback with token or error in URL
    const urlParams = new URLSearchParams(window.location.search)
    const tokenFromUrl = urlParams.get('token')
    const refreshTokenFromUrl = urlParams.get('refresh_token')
    const errorFromUrl = urlParams.get('error')
    
    if (tokenFromUrl) {
      localStorage.setItem('auth_token', tokenFromUrl)
      if (refreshTokenFromUrl) {
        localStorage.setItem('refresh_token', refreshTokenFromUrl)
      }
      localStorage.removeItem('guest_mode') // Clear guest mode if logging in
      setIsAuthenticated(true)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    } else if (errorFromUrl) {
      // Show error message
      setErrorMessage(errorFromUrl)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
      // Auto-hide error after 5 seconds
      setTimeout(() => setErrorMessage(null), 5000)
    }
  }, [])

  const handleContinueAsGuest = () => {
    localStorage.setItem('guest_mode', 'true')
    setIsAuthenticated(true)
  }

  // Loading state
  if (isAuthenticated === null) {
    return (
      <Flex h="100vh" bg="gray.900" alignItems="center" justifyContent="center">
        <Box color="gray.400">Loading...</Box>
      </Flex>
    )
  }

  // Show landing page if not authenticated
  if (!isAuthenticated) {
    return <LandingPage onContinueAsGuest={handleContinueAsGuest} />
  }

  // Show main IDE
  return (
    <Flex h="100vh" bg="gray.900" flexDirection="column">
      {/* Error Notification */}
      {errorMessage && (
        <Box
          position="fixed"
          top={4}
          right={4}
          maxW="400px"
          bg="red.600"
          color="white"
          p={4}
          borderRadius="md"
          boxShadow="lg"
          zIndex={9999}
          animation="slideInRight 0.3s ease-out"
        >
          <Flex justifyContent="space-between" alignItems="flex-start" gap={2}>
            <Box flex="1">
              <Text fontWeight="bold" fontSize="sm" mb={1}>
                Account Linking Failed
              </Text>
              <Text fontSize="xs" opacity={0.9}>
                {errorMessage}
              </Text>
            </Box>
            <Box
              as="button"
              onClick={() => setErrorMessage(null)}
              color="white"
              fontWeight="bold"
              fontSize="lg"
              cursor="pointer"
              _hover={{ opacity: 0.7 }}
              lineHeight="1"
            >
              ✕
            </Box>
          </Flex>
        </Box>
      )}

      {/* Top Header Bar */}
      <Flex
        h="50px"
        bg="gray.800"
        borderBottom="1px solid"
        borderColor="gray.700"
        px={4}
        alignItems="center"
        justifyContent="space-between"
      >
        <Text color="white" fontWeight="bold">Gunpowder Splash</Text>
        <UserMenu />
      </Flex>

      {/* Main Content Area - Temporarily simplified */}
      <Flex flex="1" overflow="hidden">
        <Sidebar onFileSelect={setSelectedFile} selectedFile={selectedFile} />
        <Box flex="1" overflow="hidden">
          <MainContent selectedFile={selectedFile} />
        </Box>
      </Flex>
    </Flex>
  )
}

export default App
