import { useState } from 'react'
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
} from '@mui/material'
import CandlestickChartIcon from '@mui/icons-material/CandlestickChart'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ListAltIcon from '@mui/icons-material/ListAlt'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SettingsIcon from '@mui/icons-material/Settings'

const navItems = [
  { icon: <CandlestickChartIcon />, label: 'Trade' },
  { icon: <SmartToyIcon />, label: 'Bot' },
  { icon: <ListAltIcon />, label: 'Orders' },
  { icon: <AssessmentIcon />, label: 'Report' },
  { icon: <SettingsIcon />, label: 'Settings' },
]

export const LeftMenuMini = () => {
  const [expanded, setExpanded] = useState(false)

  return (
    <Box
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      sx={{
        width: expanded ? 140 : 72,
        transition: 'width 0.25s ease',
        height: '100vh',
        backgroundColor: '#0b0f14',
        borderRight: '1px solid rgba(255,255,255,0.08)',
        display: 'flex',
        alignItems: 'flex-start',
        py: 4,
        position: 'sticky',
        top: 0,
      }}
    >
      <List sx={{ width: '100%' }}>
        {navItems.map((item) => (
          <Tooltip
            key={item.label}
            title={!expanded ? item.label : ''}
            placement="right"
          >
            <ListItemButton
              sx={{
                borderRadius: 3,
                mx: expanded ? 2 : 1,
                my: 0.5,
                gap: 1,
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.08)',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 0, color: 'white' }}>
                {item.icon}
              </ListItemIcon>
              {expanded && (
                <ListItemText
                  primary={
                    <Typography variant="body2" color="white">
                      {item.label}
                    </Typography>
                  }
                />
              )}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>
    </Box>
  )
}

export default LeftMenuMini

