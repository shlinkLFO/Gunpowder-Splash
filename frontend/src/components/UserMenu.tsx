import { Box, Button, Stack, Text } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import config from '../config'

interface UserInfo {
  id: string
  email: string
  display_name?: string
  avatar_url?: string
  provider: string
}

export default function UserMenu() {
  const [showMenu, setShowMenu] = useState(false)
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [isGuest, setIsGuest] = useState(false)

  useEffect(() => {
    // Check if guest mode
    const guestMode = localStorage.getItem('guest_mode')
    if (guestMode === 'true') {
      setIsGuest(true)
      return
    }

    // Fetch user info if authenticated
    const token = localStorage.getItem('auth_token')
    if (token) {
      fetchUserInfo(token)
    }
  }, [])

  const fetchUserInfo = async (token: string) => {
    try {
      const apiUrl = config.apiBaseUrl || '/api'
      const response = await fetch(`${apiUrl}/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUserInfo(data)
      } else if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        window.location.reload()
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  const handleLogin = (provider: 'google' | 'github') => {
    const apiUrl = config.apiBaseUrl || '/api'
    window.location.href = `${apiUrl}/v1/auth/login/${provider}`
  }

  const handleGuestMode = () => {
    localStorage.setItem('guest_mode', 'true')
    window.location.reload()
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('guest_mode')
    window.location.reload()
  }

  // If authenticated or guest mode, show profile avatar
  if (userInfo || isGuest) {
    const displayName = userInfo?.display_name || userInfo?.email || 'Guest'
    const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    
    return (
      <Box position="relative">
        <Box
          as="button"
          cursor="pointer"
          onClick={() => setShowMenu(!showMenu)}
          _hover={{ opacity: 0.8 }}
          w="32px"
          h="32px"
          borderRadius="full"
          overflow="hidden"
          bg="blue.500"
          display="flex"
          alignItems="center"
          justifyContent="center"
          color="white"
          fontSize="sm"
          fontWeight="semibold"
        >
          {userInfo?.avatar_url ? (
            <img 
              src={userInfo.avatar_url} 
              alt={displayName}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : (
            initials
          )}
        </Box>

        {showMenu && (
          <Box
            position="absolute"
            right={0}
            top="calc(100% + 8px)"
            bg="gray.800"
            borderRadius="md"
            borderWidth="1px"
            borderColor="gray.700"
            p={4}
            minW="250px"
            zIndex={1000}
          >
            {userInfo ? (
              <Stack gap={2}>
                <Text color="white" fontWeight="semibold">
                  {userInfo.display_name || userInfo.email.split('@')[0]}
                </Text>
                <Text color="gray.400" fontSize="xs">
                  {userInfo.email}
                </Text>
                <Text color="gray.500" fontSize="xs">
                  Signed in with {userInfo.provider === 'google' ? 'Google' : 'GitHub'}
                </Text>
                
                {/* Account linking buttons */}
                {userInfo.provider === 'google' ? (
                  <Button
                    onClick={() => handleLogin('github')}
                    width="100%"
                    size="sm"
                    colorScheme="gray"
                    variant="outline"
                  >
                    Link GitHub Account
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleLogin('google')}
                    width="100%"
                    size="sm"
                    colorScheme="red"
                    variant="outline"
                  >
                    Link Google Account
                  </Button>
                )}
                
                <Button
                  onClick={handleLogout}
                  width="100%"
                  variant="outline"
                  size="sm"
                  colorScheme="red"
                  mt={2}
                >
                  Log Out
                </Button>
              </Stack>
            ) : (
              <Stack gap={2}>
                <Text color="gray.400" fontSize="sm">
                  Guest Mode
                </Text>
                <Button
                  onClick={() => handleLogin('google')}
                  width="100%"
                  colorScheme="red"
                  size="sm"
                >
                  Login with Google
                </Button>
                <Button
                  onClick={() => handleLogin('github')}
                  width="100%"
                  colorScheme="gray"
                  size="sm"
                >
                  Login with GitHub
                </Button>
              </Stack>
            )}
          </Box>
        )}
      </Box>
    )
  }

  // Not authenticated - show login button
  return (
    <Box position="relative">
      <Button
        onClick={() => setShowMenu(!showMenu)}
        size="sm"
        colorScheme="blue"
      >
        Log In
      </Button>

      {showMenu && (
        <Box
          position="absolute"
          right={0}
          top="calc(100% + 8px)"
          bg="gray.800"
          borderRadius="md"
          borderWidth="1px"
          borderColor="gray.700"
          p={4}
          minW="250px"
          zIndex={1000}
        >
          <Stack gap={2}>
            <Button
              onClick={() => handleLogin('google')}
              width="100%"
              colorScheme="red"
              size="sm"
            >
              Login with Google
            </Button>
            <Button
              onClick={() => handleLogin('github')}
              width="100%"
              colorScheme="gray"
              size="sm"
            >
              Login with GitHub
            </Button>
            <Button
              onClick={handleGuestMode}
              width="100%"
              variant="outline"
              size="sm"
            >
              Continue as Guest
            </Button>
          </Stack>
        </Box>
      )}
    </Box>
  )
}
