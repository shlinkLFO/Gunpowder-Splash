import { Box, Flex, Text, Button } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import UserMenu from './components/UserMenu'
import CodeEditor from './components/tabs/CodeEditor'
import WebEdit from './components/tabs/WebEdit'
import DataExplorer from './components/tabs/DataExplorer'
import QueryFilter from './components/tabs/QueryFilter'
import Templates from './components/tabs/Templates'
import History from './components/tabs/History'
import System from './components/tabs/System'

type Tab = 'code-editor' | 'web-edit' | 'data-explorer' | 'query-filter' | 'templates' | 'history' | 'system'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('code-editor')
  const [isGuest, setIsGuest] = useState(false)
  const [showLoginPage, setShowLoginPage] = useState(false)

  useEffect(() => {
    // Check for auth token or guest mode
    const token = localStorage.getItem('auth_token')
    const guestMode = localStorage.getItem('guest_mode')
    
    if (token) {
      setIsAuthenticated(true)
      setIsGuest(false)
    } else if (guestMode === 'true') {
      setIsAuthenticated(true)
      setIsGuest(true)
    } else {
      setIsAuthenticated(false)
      setIsGuest(false)
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
      setIsGuest(false) // No longer a guest
      setShowLoginPage(false) // Close login page if open
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
    setIsGuest(true)
  }

  const handleLoginClick = () => {
    setShowLoginPage(true)
  }

  const handleBackFromLogin = () => {
    setShowLoginPage(false)
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: 'code-editor', label: 'Code Editor' },
    { id: 'web-edit', label: 'Web-Edit' },
    { id: 'data-explorer', label: 'Data Explorer' },
    { id: 'query-filter', label: 'Query & Filter' },
    { id: 'templates', label: 'Templates' },
    { id: 'history', label: 'History' },
    { id: 'system', label: 'System' },
  ]

  // Loading state
  if (isAuthenticated === null) {
    return (
      <Flex h="100vh" bg="gray.900" alignItems="center" justifyContent="center">
        <Box color="gray.400">Loading...</Box>
      </Flex>
    )
  }

  // Show login page if guest user clicks "Log In"
  if (showLoginPage) {
    return <LoginPage onBack={handleBackFromLogin} />
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
          top="16px"
          right="16px"
          maxW="400px"
          backgroundColor="#374151"
          color="#ffffff"
          p="20px"
          borderRadius="8px"
          boxShadow="0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3)"
          border="2px solid #4B5563"
          zIndex={9999}
          style={{
            animation: 'slideInRight 0.3s ease-out'
          }}
        >
          <Flex justifyContent="space-between" alignItems="flex-start" gap="12px">
            <Box flex="1">
              <Text fontWeight="bold" fontSize="sm" mb="8px" color="#F87171">
                Account Linking Failed
              </Text>
              <Text fontSize="xs" color="#D1D5DB" lineHeight="1.5">
                {errorMessage}
              </Text>
            </Box>
            <Box
              as="button"
              onClick={() => setErrorMessage(null)}
              color="#9CA3AF"
              fontWeight="bold"
              fontSize="xl"
              cursor="pointer"
              _hover={{ color: '#ffffff' }}
              lineHeight="1"
              ml="8px"
            >
              ✕
            </Box>
          </Flex>
        </Box>
      )}

      {/* Top Header Bar with Navigation */}
      <Flex
        h="50px"
        bg="gray.800"
        borderBottom="1px solid"
        borderColor="gray.700"
        px={4}
        alignItems="center"
        gap={6}
      >
        {/* Logo */}
        <Text color="white" fontWeight="bold" fontSize="lg" whiteSpace="nowrap">
          Gunpowder Splash
        </Text>

        {/* Navigation Tabs */}
        <Flex flex="1" gap={1} overflow="auto">
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              size="sm"
              variant={activeTab === tab.id ? 'solid' : 'ghost'}
              colorScheme={activeTab === tab.id ? 'blue' : 'gray'}
              color={activeTab === tab.id ? 'white' : 'gray.300'}
              _hover={{ color: 'white', bg: activeTab === tab.id ? 'blue.600' : 'gray.700' }}
              whiteSpace="nowrap"
            >
              {tab.label}
            </Button>
          ))}
        </Flex>

        {/* User Menu or Login Button */}
        {isGuest ? (
          <Button
            onClick={handleLoginClick}
            size="sm"
            colorScheme="blue"
            whiteSpace="nowrap"
          >
            Log In
          </Button>
        ) : (
          <UserMenu />
        )}
      </Flex>

      {/* Main Content Area */}
      <Box flex="1" overflow="hidden">
        {activeTab === 'code-editor' && <CodeEditor />}
        {activeTab === 'web-edit' && <WebEdit />}
        {activeTab === 'data-explorer' && <DataExplorer />}
        {activeTab === 'query-filter' && <QueryFilter />}
        {activeTab === 'templates' && <Templates />}
        {activeTab === 'history' && <History />}
        {activeTab === 'system' && <System />}
      </Box>
    </Flex>
  )
}

export default App
