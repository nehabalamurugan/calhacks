"use client"

"use client";

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "./ui/card"
import { X } from "lucide-react"

interface Person {
  id: string
  name: string
  company: string
  conversationSummary: string
  size: "small" | "medium" | "large"
  position: number // percentage along timeline
  date: string
  person_id?: string
  created_at?: string
}

interface ConversationMessage {
  speaker: string
  message: string
}

interface Conversation {
  id: number | string
  name: string
  company: string
  date: string
  conversation: ConversationMessage[]
}

const circleSize = "w-40 h-40"

interface TimelineProps {
  onConversationChange?: (isOpen: boolean) => void;
  onInteraction?: () => void;
}

export function Timeline({ onConversationChange, onInteraction }: TimelineProps = {}) {
  const [hoveredPerson, setHoveredPerson] = useState<Person | null>(null)
  const [scrollPosition, setScrollPosition] = useState(0)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [selectedCircleId, setSelectedCircleId] = useState<string | null>(null)
  const [hideTitle, setHideTitle] = useState(false)
  const [peopleData, setPeopleData] = useState<Person[]>([])
  const [loading, setLoading] = useState(true)
  const timelineRef = useRef<HTMLDivElement>(null)

  // Fetch real data from backend on component mount
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        console.log('Fetching conversations from backend...')
        const response = await fetch('http://localhost:5001/api/conversations?limit=50')
        const data = await response.json()
        
        console.log('Backend response:', data)
        
        if (data.success && data.conversations && data.conversations.length > 0) {
          // Format conversations for timeline display
          const formattedPeople = data.conversations.map((conv: any, index: number) => {
            // Generate summary from conversation turns
            const summary = conv.turns_preview && conv.turns_preview.length > 0 
              ? conv.turns_preview.map((turn: any) => turn.content).join(' ').slice(0, 150)
              : 'No conversation content available'
            
            // Format date
            const date = new Date(conv.created_at)
            const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            
            // Determine size based on turn count
            let size: "small" | "medium" | "large" = "small"
            if (conv.total_turns > 10) size = "large"
            else if (conv.total_turns > 5) size = "medium"
            
            // Position evenly distributed along timeline
            const position = Math.min(6 + (index * 6), 96)
            
            return {
              id: conv.id,
              name: conv.person_name || 'Unknown',
              company: conv.person_affiliation || 'Unknown',
              conversationSummary: summary,
              size: size,
              position: position,
              date: formattedDate,
              person_id: conv.person_id,
              created_at: conv.created_at
            }
          })
          
          console.log('Formatted people data:', formattedPeople)
          setPeopleData(formattedPeople)
        } else {
          console.log('No conversations found or API returned empty data')
          // Set empty array if no data
          setPeopleData([])
        }
      } catch (error) {
        console.error('Error fetching conversations:', error)
        // Set empty array on error
        setPeopleData([])
      } finally {
        setLoading(false)
      }
    }
    
    fetchConversations()
  }, [])

  const handleCircleClick = async (person: Person) => {
    // Trigger interaction callback
    onInteraction?.();
    
    try {
      // Fetch conversation data from backend using conversation_id (which is person.id in our case)
      const response = await fetch(`http://localhost:5001/api/conversations?limit=50`);
      const data = await response.json();
      
      if (data.success && data.conversations.length > 0) {
        // Find the conversation with matching id
        const conv = data.conversations.find((c: any) => c.id === person.id);
        
        if (conv && conv.turns_preview.length > 0) {
          const conversation: Conversation = {
            id: parseInt(conv.id),
            name: conv.person_name || person.name,
            company: conv.person_affiliation || person.company,
            date: conv.created_at || person.created_at,
            conversation: conv.turns_preview.map((turn: any) => ({
              speaker: turn.speaker_label || turn.speaker_type || 'Speaker',
              message: turn.content
            }))
          };
          setSelectedConversation(conversation);
        } else {
          // No turns available, show summary
          const conversation: Conversation = {
            id: parseInt(person.id),
            name: person.name,
            company: person.company,
            date: person.date,
            conversation: [
              { speaker: person.name, message: person.conversationSummary }
            ]
          };
          setSelectedConversation(conversation);
        }
      } else {
        // No conversations found, show summary
        const conversation: Conversation = {
          id: parseInt(person.id),
          name: person.name,
          company: person.company,
          date: person.date,
          conversation: [
            { speaker: person.name, message: person.conversationSummary }
          ]
        };
        setSelectedConversation(conversation);
      }
    } catch (error) {
      console.error('Error fetching conversation:', error);
      // Fallback to summary on error
      const conversation: Conversation = {
        id: parseInt(person.id),
        name: person.name,
        company: person.company,
        date: person.date,
        conversation: [
          { speaker: person.name, message: person.conversationSummary }
        ]
      };
      setSelectedConversation(conversation);
    }
    
    setSelectedCircleId(person.id);
  };

  const handleCloseConversation = () => {
    setSelectedConversation(null);
    setSelectedCircleId(null);
    setHideTitle(false);
  };
  
  // Update hideTitle when conversation opens and notify parent
  useEffect(() => {
    if (selectedConversation) {
      setHideTitle(true);
      onConversationChange?.(true);
    } else {
      setHideTitle(false);
      onConversationChange?.(false);
    }
  }, [selectedConversation, onConversationChange]);

  useEffect(() => {
    const handleScroll = () => {
      if (timelineRef.current) {
        const scrollLeft = timelineRef.current.scrollLeft
        const scrollWidth = timelineRef.current.scrollWidth
        const clientWidth = timelineRef.current.clientWidth
        
        // Continuous scroll - when reaching the end, loop back to start
        if (scrollLeft >= scrollWidth - clientWidth - 100) {
          timelineRef.current.scrollLeft = 0
        }
        
        setScrollPosition(scrollLeft)
      }
    }

    const timeline = timelineRef.current
    if (timeline) {
      timeline.addEventListener('scroll', handleScroll)
      return () => timeline.removeEventListener('scroll', handleScroll)
    }
  }, [])

  return (
    <div className="relative h-full">
      
      {/* Scrollable timeline container */}
      <div 
        ref={timelineRef}
        className="relative h-full overflow-x-auto overflow-y-hidden scrollbar-hide timeline-scroll"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-white/60">Loading conversations...</div>
          </div>
        )}
        
        {!loading && peopleData.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-white/60">No conversations found. Make sure the backend is running on port 5001.</div>
          </div>
        )}
        
        <div className="relative h-full" style={{ width: '400vw' }}>
          {/* Timeline nodes */}
          {peopleData.map((person) => (
            <motion.div
              key={person.id}
              className="absolute top-1/2 transform -translate-y-1/2 cursor-pointer group"
              style={{ left: `${person.position}%` }}
              onMouseEnter={() => setHoveredPerson(person)}
              onMouseLeave={() => setHoveredPerson(null)}
            >
              {/* Circle node with click handler */}
              <div 
                className={`${circleSize} bg-gradient-to-br ${
                  selectedCircleId === person.id 
                    ? 'from-black to-black' 
                    : 'from-black/50 to-black/60'
                } rounded-full shadow-xl border-2 border-white/30 relative z-10 flex flex-col items-center justify-center p-2 transition-all duration-300 cursor-pointer`}
                onClick={() => handleCircleClick(person)}
              >
                {/* Default state: Name and date */}
                <div className="flex flex-col items-center justify-center">
                  <div className="text-white text-xs font-bold mb-1 leading-tight">
                    {person.name}
                  </div>
                  <span className="text-white/80 text-xs font-medium">
                    {person.date}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Conversation Box */}
      <AnimatePresence>
        {selectedConversation && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
          >
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm pointer-events-auto" onClick={handleCloseConversation}></div>
            
            {/* Conversation Panel */}
            <div className="relative w-96 max-h-80 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-4 overflow-y-auto pointer-events-auto">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-white font-semibold">{selectedConversation.name}</h3>
                <button 
                  onClick={handleCloseConversation}
                  className="text-white/60 hover:text-white transition-colors duration-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-3">
                {selectedConversation.conversation.map((message, index) => (
                  <div key={index} className={`p-3 rounded-lg ${
                    message.speaker === 'Ina' || message.speaker === 'Neha'
                      ? 'bg-blue-500/20 ml-8' 
                      : 'bg-white/10 mr-8'
                  }`}>
                    <div className="text-xs text-white/60 mb-1">{message.speaker || 'Speaker'}</div>
                    <div className="text-white text-sm">{message.message}</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scroll hint */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-white/70 bg-black/20 backdrop-blur-sm px-3 py-1 rounded-full">
        ← Scroll →
      </div>
    </div>
  )
}
