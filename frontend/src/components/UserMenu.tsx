import { Box, Button, Stack, Text } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { FiLogIn, FiLogOut, FiUser } from 'react-icons/fi'
import { FaGoogle, FaGithub } from 'react-icons/fa'
import config from '../config'

interface User {
  id: string
  email: string
  display_name?: string
  avatar_url?: string
  provider: string
}

export default function UserMenu() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [isGuest, setIsGuest] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('[data-user-menu]')) {
        setShowLogin(false)
        setShowMenu(false)
      }
    }

    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  const checkAuthStatus = async () => {
    try {
      setError(null)
      const token = localStorage.getItem('auth_token')
      const guestMode = localStorage.getItem('guest_mode')

      if (guestMode === 'true') {
        setIsGuest(true)
        setLoading(false)
        return
      }

      if (token) {
        try {
          const apiUrl = config.apiBaseUrl || '/api'
          const response = await fetch(`${apiUrl}/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          })

          if (response.ok) {
            const data = await response.json()
            setUser(data)
          } else {
            console.log('Auth token invalid, clearing')
            localStorage.removeItem('auth_token')
          }
        } catch (fetchError) {
          console.error('Failed to fetch user info:', fetchError)
          // Don't remove token on network error, just continue
        }
      }
    } catch (error) {
      console.error('Error in checkAuthStatus:', error)
      setError('Failed to check auth status')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = (provider: 'google' | 'github') => {
    try {
      const apiUrl = config.apiBaseUrl || '/api'
      window.location.href = `${apiUrl}/v1/auth/login/${provider}`
    } catch (error) {
      console.error('Login redirect failed:', error)
      setError('Failed to redirect to login')
    }
  }

  const handleGuestMode = () => {
    try {
      localStorage.setItem('guest_mode', 'true')
      setIsGuest(true)
      setShowLogin(false)
    } catch (error) {
      console.error('Failed to set guest mode:', error)
      setError('Failed to enter guest mode')
    }
  }

  const handleLogout = () => {
    try {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('guest_mode')
      setUser(null)
      setIsGuest(false)
      setShowMenu(false)
      window.location.reload()
    } catch (error) {
      console.error('Logout failed:', error)
      setError('Failed to log out')
    }
  }

  if (loading) {
    return (
      <Text fontSize="sm" color="gray.400">
        Loading...
      </Text>
    )
  }

  if (error) {
    return (
      <Text fontSize="sm" color="red.400">
        {error}
      </Text>
    )
  }

  // Show login button for non-authenticated users
  if (!user && !isGuest) {
    return (
      <Box position="relative" data-user-menu>
        <Button
          onClick={(e) => {
            e.stopPropagation()
            setShowLogin(!showLogin)
          }}
          size="sm"
          variant="outline"
          colorScheme="blue"
        >
          <FiLogIn style={{ marginRight: '8px' }} />
          Log In
        </Button>

        {showLogin && (
          <Box
            position="absolute"
            right={0}
            top="calc(100% + 8px)"
            bg="gray.800"
            borderRadius="md"
            borderWidth="1px"
            borderColor="gray.700"
            p={4}
            minW="280px"
            boxShadow="dark-lg"
            zIndex={1000}
          >
            <Text color="white" mb={3} fontWeight="medium">
              Log in to Gunpowder Splash
            </Text>
            <Stack gap={2}>
              <Button
                onClick={() => handleLogin('google')}
                width="100%"
                colorScheme="red"
                size="sm"
              >
                <FaGoogle style={{ marginRight: '8px' }} />
                Continue with Google
              </Button>
              <Button
                onClick={() => handleLogin('github')}
                width="100%"
                colorScheme="gray"
                size="sm"
              >
                <FaGithub style={{ marginRight: '8px' }} />
                Continue with GitHub
              </Button>
              <Button
                onClick={handleGuestMode}
                width="100%"
                variant="ghost"
                size="sm"
                mt={2}
              >
                Continue as Guest
              </Button>
            </Stack>
          </Box>
        )}
      </Box>
    )
  }

  // Show guest or user menu
  const displayName = user?.display_name || (isGuest ? 'Guest' : user?.email?.split('@')[0] || 'User')
  const avatarUrl = user?.avatar_url

  return (
    <Box position="relative" data-user-menu>
      <Stack
        direction="row"
        align="center"
        gap={2}
        cursor="pointer"
        onClick={(e) => {
          e.stopPropagation()
          setShowMenu(!showMenu)
        }}
        _hover={{ opacity: 0.8 }}
        px={2}
        py={1}
        borderRadius="md"
      >
        {avatarUrl ? (
          <Box
            w="32px"
            h="32px"
            borderRadius="full"
            overflow="hidden"
            bg="gray.600"
          >
            <img
              src={avatarUrl}
              alt={displayName}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </Box>
        ) : (
          <Box
            w="32px"
            h="32px"
            borderRadius="full"
            bg="blue.600"
            display="flex"
            alignItems="center"
            justifyContent="center"
            color="white"
            fontSize="sm"
            fontWeight="bold"
          >
            {isGuest ? <FiUser /> : displayName?.charAt(0).toUpperCase()}
          </Box>
        )}
        <Text fontSize="sm" color="white" display={{ base: 'none', md: 'block' }}>
          {displayName}
        </Text>
      </Stack>

      {showMenu && (
        <Box
          position="absolute"
          right={0}
          top="calc(100% + 8px)"
          bg="gray.800"
          borderRadius="md"
          borderWidth="1px"
          borderColor="gray.700"
          minW="240px"
          boxShadow="dark-lg"
          zIndex={1000}
        >
          {user && (
            <Box p={4} borderBottomWidth="1px" borderColor="gray.700">
              <Text fontSize="sm" fontWeight="bold" color="white">
                {user.display_name || 'User'}
              </Text>
              <Text fontSize="xs" color="gray.400">
                {user.email}
              </Text>
              <Text fontSize="xs" color="gray.500" mt={1}>
                via {user.provider}
              </Text>
            </Box>
          )}

          {isGuest && (
            <>
              <Box
                p={3}
                cursor="pointer"
                _hover={{ bg: 'gray.700' }}
                color="white"
                onClick={(e) => {
                  e.stopPropagation()
                  setShowMenu(false)
                  setShowLogin(true)
                }}
              >
                <Stack direction="row" align="center" gap={2}>
                  <FiLogIn />
                  <Text fontSize="sm">Log in to save work</Text>
                </Stack>
              </Box>
              <Box
                height="1px"
                bg="gray.700"
              />
            </>
          )}

          <Box
            p={3}
            cursor="pointer"
            _hover={{ bg: 'gray.700' }}
            color="red.400"
            onClick={(e) => {
              e.stopPropagation()
              handleLogout()
            }}
          >
            <Stack direction="row" align="center" gap={2}>
              <FiLogOut />
              <Text fontSize="sm">
                {isGuest ? 'Exit Guest Mode' : 'Log Out'}
              </Text>
            </Stack>
          </Box>
        </Box>
      )}
    </Box>
  )
}
