"use client"

import { motion } from "framer-motion"
import { Building2, Calendar, MessageSquare } from "lucide-react"

interface Interaction {
  date: string
  summary: string
  location: string
}

interface Person {
  id: string
  name: string
  company: string
  role: string
  interactions: Interaction[]
  imageUrl: string
}

interface PeopleTilesProps {
  searchQuery: string
}

const PEOPLE_DATA: Person[] = [
  {
    id: "1",
    name: "Sarah Chen",
    company: "TechCorp",
    role: "VP of Engineering",
    imageUrl: "/placeholder.svg?height=100&width=100",
    interactions: [
      {
        date: "2024-01-15",
        summary: "Discussed AI integration strategies and potential collaboration opportunities",
        location: "San Francisco, CA",
      },
      {
        date: "2024-02-03",
        summary: "Follow-up on partnership proposal, reviewed technical requirements",
        location: "Virtual Meeting",
      },
    ],
  },
  {
    id: "2",
    name: "Marcus Johnson",
    company: "StartupXYZ",
    role: "Founder & CEO",
    imageUrl: "/placeholder.svg?height=100&width=100",
    interactions: [
      {
        date: "2024-01-20",
        summary: "Pitched new product idea, explored funding opportunities",
        location: "New York, NY",
      },
      { date: "2024-02-10", summary: "Demo of MVP, discussed go-to-market strategy", location: "New York, NY" },
      {
        date: "2024-03-05",
        summary: "Investor introduction meeting, next steps planning",
        location: "Virtual Meeting",
      },
    ],
  },
  {
    id: "3",
    name: "Emily Rodriguez",
    company: "DesignHub",
    role: "Creative Director",
    imageUrl: "/placeholder.svg?height=100&width=100",
    interactions: [
      { date: "2024-01-25", summary: "Brainstormed UX improvements for mobile app redesign", location: "Austin, TX" },
    ],
  },
  {
    id: "4",
    name: "David Kim",
    company: "AI Labs",
    role: "Research Scientist",
    imageUrl: "/placeholder.svg?height=100&width=100",
    interactions: [
      {
        date: "2024-02-01",
        summary: "Presented latest research on neural networks and applications",
        location: "Boston, MA",
      },
      {
        date: "2024-02-28",
        summary: "Collaborative research discussion, potential paper co-authoring",
        location: "Boston, MA",
      },
    ],
  },
  {
    id: "5",
    name: "Lisa Wang",
    company: "CloudNet",
    role: "CTO",
    imageUrl: "/placeholder.svg?height=100&width=100",
    interactions: [
      {
        date: "2024-02-12",
        summary: "Infrastructure scaling discussion, cloud architecture review",
        location: "Seattle, WA",
      },
      { date: "2024-03-01", summary: "Security audit findings and recommendations", location: "Virtual Meeting" },
    ],
  },
  {
    id: "6",
    name: "James Brown",
    company: "DataFlow",
    role: "Head of Analytics",
    imageUrl: "/placeholder.svg?height=100&width=100",
    interactions: [
      {
        date: "2024-02-20",
        summary: "Data pipeline optimization strategies and best practices",
        location: "Chicago, IL",
      },
    ],
  },
]

export const PeopleTiles = ({ searchQuery }: PeopleTilesProps) => {
  const filteredPeople = PEOPLE_DATA.filter(
    (person) =>
      person.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      person.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      person.role.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div className="w-full max-h-[65vh] overflow-y-auto px-4 pb-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredPeople.map((person, index) => (
          <motion.div
            key={person.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="backdrop-blur-xl bg-white/20 border-2 border-white/30 rounded-2xl p-5 hover:bg-white/30 transition-all cursor-pointer"
          >
            <div className="flex gap-4 mb-4">
              <img
                src={person.imageUrl || "/placeholder.svg"}
                alt={person.name}
                className="w-16 h-16 rounded-full object-cover border-2 border-white/40"
              />
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-foreground truncate">{person.name}</h3>
                <div className="flex items-center gap-1.5 text-sm text-foreground/80">
                  <Building2 className="w-3.5 h-3.5" />
                  <span className="truncate">{person.company}</span>
                </div>
                <p className="text-sm text-foreground/70 truncate">{person.role}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-foreground/80">
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="font-medium">
                  {person.interactions.length} {person.interactions.length === 1 ? "interaction" : "interactions"}
                </span>
              </div>

              <div className="space-y-2">
                {person.interactions.map((interaction, idx) => (
                  <div key={idx} className="bg-white/10 rounded-lg p-3 border border-white/20">
                    <div className="flex items-center gap-2 mb-1.5">
                      <Calendar className="w-3.5 h-3.5 text-foreground/60" />
                      <span className="text-xs text-foreground/70 font-medium">
                        {new Date(interaction.date).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </span>
                      <span className="text-xs text-foreground/60">•</span>
                      <span className="text-xs text-foreground/60">{interaction.location}</span>
                    </div>
                    <p className="text-sm text-foreground/80 leading-relaxed">{interaction.summary}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredPeople.length === 0 && (
        <div className="flex items-center justify-center h-40">
          <p className="text-foreground/60 text-lg">No people found matching your search</p>
        </div>
      )}
    </div>
  )
}
