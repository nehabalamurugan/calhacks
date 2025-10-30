"use client";

import { Footer } from "@/components/footer";
import { Timeline } from "@/components/timeline";
import { useState } from "react";

interface SearchResult {
  name: string;
  company: string;
  date: string;
  summary: string;
  relevance_score: number;
}

interface SearchResponse {
  success: boolean;
  message: string;
  results: SearchResult[];
  query: string;
}

interface Person {
  id: number;
  name: string;
  company: string;
}

interface Conversation {
  id: number;
  name: string;
  company: string;
  date: string;
  summary: string;
}

interface FilterState {
  person_id?: number;
  conversation_id?: number;
  start_time?: string;
  end_time?: string;
}

export default function Home() {
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchMessage, setSearchMessage] = useState("");
  
  // Filter states
  const [activeFilter, setActiveFilter] = useState<'person' | 'date' | 'conversation' | null>(null);
  const [people, setPeople] = useState<Person[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [filters, setFilters] = useState<FilterState>({});
  const [isLoadingPeople, setIsLoadingPeople] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  
  // Track if any interaction has happened
  const [hasInteracted, setHasInteracted] = useState(false);
  const [isConversationOpen, setIsConversationOpen] = useState(false);

  const scrollToSearch = () => {
    console.log('Going to search');
    setShowSearch(true);
    setHasInteracted(true);
    // Reset search query and results when going to search
    setSearchQuery("");
    setSearchResults([]);
    setSearchMessage("");
    setActiveFilter(null);
    setFilters({});
  };

  const scrollToTimeline = () => {
    console.log('Going back to timeline');
    console.log('Current showSearch state:', showSearch);
    console.log('Current isConversationOpen state:', isConversationOpen);
    setShowSearch(false);
    // Clear search results when going back
    setSearchResults([]);
    setSearchQuery("");
    setSearchMessage("");
    setActiveFilter(null);
    setFilters({});
    // Also reset conversation state to ensure clean timeline view
    setIsConversationOpen(false);
  };

  const fetchPeople = async () => {
    setIsLoadingPeople(true);
    try {
      const response = await fetch('http://localhost:5001/api/people');
      const data = await response.json();
      if (data.success) {
        setPeople(data.people);
      }
    } catch (error) {
      console.error('Error fetching people:', error);
    } finally {
      setIsLoadingPeople(false);
    }
  };

  const fetchConversations = async () => {
    setIsLoadingConversations(true);
    try {
      const params = new URLSearchParams();
      if (filters.person_id) params.append('person_id', filters.person_id.toString());
      if (filters.start_time) params.append('start_time', filters.start_time);
      if (filters.end_time) params.append('end_time', filters.end_time);
      
      const response = await fetch(`http://localhost:5001/api/conversations?${params}`);
      const data = await response.json();
      if (data.success) {
        setConversations(data.conversations);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleFilterClick = (filterType: 'person' | 'date' | 'conversation') => {
    setHasInteracted(true);
    
    if (activeFilter === filterType) {
      setActiveFilter(null);
      return;
    }
    
    setActiveFilter(filterType);
    
    if (filterType === 'person') {
      fetchPeople();
    } else if (filterType === 'conversation') {
      fetchConversations();
    }
  };

  const handlePersonSelect = (person: Person) => {
    setFilters(prev => ({ ...prev, person_id: person.id }));
    setActiveFilter(null);
    setHasInteracted(true);
  };

  const handleConversationSelect = (conversation: Conversation) => {
    setFilters(prev => ({ ...prev, conversation_id: conversation.id }));
    setActiveFilter(null);
    setHasInteracted(true);
  };

  const handleDateChange = (type: 'start' | 'end', value: string) => {
    setFilters(prev => ({ ...prev, [`${type}_time`]: value }));
    setHasInteracted(true);
  };

  const clearFilters = () => {
    setFilters({});
    setActiveFilter(null);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setHasInteracted(true);
    setIsSearching(true);
    setSearchMessage("");
    
    try {
      const response = await fetch('http://localhost:5001/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: searchQuery,
          ...filters
        }),
      });
      
      const data: SearchResponse = await response.json();
      
      if (data.success) {
        setSearchResults(data.results);
        setSearchMessage(data.message);
      } else {
        setSearchMessage(data.message);
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchMessage("Error connecting to search service. Please try again.");
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <main className="h-[100dvh] w-full overflow-hidden">
      <div className="relative h-full w-full">
        {/* Beautiful gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-[42px] md:rounded-[72px]" />
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-900/20 via-transparent to-purple-900/20 rounded-[42px] md:rounded-[72px]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-600/10 via-transparent to-purple-600/10 rounded-[42px] md:rounded-[72px]" />
        
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden rounded-[42px] md:rounded-[72px]">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-purple-500/5 to-blue-500/5 rounded-full blur-3xl animate-pulse delay-500" />
        </div>
        
        {/* Main content */}
        <div className="relative z-10 flex flex-col h-full">
          {/* Compact Header - shown when interacted */}
          {hasInteracted && (
            <div className="flex-shrink-0 p-6">
              <div className="flex flex-col items-center">
                <h1 className="text-3xl md:text-4xl font-serif italic text-white/90 tracking-wider mb-4">
                  Recall
                </h1>
                <button 
                  onClick={() => {
                    console.log('Arrow clicked! Current showSearch:', showSearch);
                    if (showSearch) {
                      scrollToTimeline();
                    } else {
                      scrollToSearch();
                    }
                  }}
                  className="text-white/60 hover:text-white/90 transition-colors duration-300"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {showSearch ? (
                      // Up arrow when in search view
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    ) : (
                      // Down arrow when in timeline view
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    )}
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Artsy Recall Title - shown when not interacted */}
          {!hasInteracted && (
            <div className="flex-1 flex flex-col items-center justify-center">
              <h1 className="text-8xl md:text-9xl lg:text-[12rem] font-serif italic text-white/90 tracking-wider cursor-default">
                Recall
              </h1>
              <p className="text-xl md:text-2xl text-white/70 font-light mt-4 tracking-wide">
                Work hard, network harder.
              </p>
              
              {/* Arrow button */}
              <button 
                onClick={scrollToSearch}
                className="mt-8 text-white/60 hover:text-white/90 transition-colors duration-300"
              >
                <svg className="w-8 h-8 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              </button>
            </div>
          )}
          
          {/* Timeline */}
          <div className={`${hasInteracted ? 'flex-1' : 'h-1/2'} pb-4 transition-all duration-500 ${showSearch ? 'opacity-0 -translate-y-full' : 'opacity-100 translate-y-0'}`}>
            <Timeline 
              onInteraction={() => setHasInteracted(true)} 
              onConversationChange={setIsConversationOpen}
            />
          </div>
          
          {/* Search Section */}
          <div 
            id="search-section"
            className={`absolute bottom-0 left-0 right-0 transition-all duration-500 ${showSearch ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-full'}`}
          >
            <div className="p-8">
              <div className="max-w-4xl mx-auto">
                {/* Search Results Display */}
                {(isSearching || (searchResults && searchResults.length > 0) || searchMessage) && (
                  <div className="mb-6 p-6 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl max-h-96 flex flex-col">
                    {/* Query Display */}
                    {searchQuery && (
                      <div className="mb-4 flex-shrink-0">
                        <p className="text-white/90 font-semibold text-xl">{searchQuery}</p>
                      </div>
                    )}
                    
                    {/* Loading Indicator */}
                    {isSearching && !searchMessage && !searchResults && (
                      <div className="mb-4 flex-shrink-0">
                        <p className="text-white/60">Searching...</p>
                      </div>
                    )}
                    
                    {/* Search Message */}
                    {searchMessage && (
                      <div className="mb-4 flex-shrink-0">
                        <p className="text-white/90 text-base leading-relaxed whitespace-pre-wrap">{searchMessage}</p>
                      </div>
                    )}
                    
                    {/* Search Results - Scrollable */}
                    {searchResults && searchResults.length > 0 && (
                      <div className="flex-1 overflow-hidden">
                        <h3 className="text-lg font-bold text-white mb-3 flex-shrink-0">Results:</h3>
                        <div className="space-y-3 overflow-y-auto max-h-64 pr-2 pb-2 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                          {searchResults.map((result, index) => (
                            <div key={index} className="p-3 bg-white/5 rounded-lg border border-white/10 flex-shrink-0">
                              <div className="flex justify-between items-start mb-2">
                                <div>
                                  <h4 className="text-white font-semibold text-sm">{result.name}</h4>
                                  <p className="text-white/70 text-xs">{result.company} • {result.date}</p>
                                </div>
                                <div className="text-white/50 text-xs">
                                  Score: {result.relevance_score}
                                </div>
                              </div>
                              <p className="text-white/80 text-xs leading-relaxed line-clamp-2">{result.summary}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Filter Panel */}
                {activeFilter && (
                  <div className="mb-4 p-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl">
                    {activeFilter === 'person' && (
                      <div>
                        <h3 className="text-white font-semibold mb-3">Select a Person</h3>
                        <div className="max-h-48 overflow-y-auto space-y-2">
                          {isLoadingPeople ? (
                            <div className="text-white/60 text-center py-4">Loading people...</div>
                          ) : (
                            people.map((person) => (
                              <button
                                key={person.id}
                                onClick={() => handlePersonSelect(person)}
                                className="w-full p-3 bg-white/5 hover:bg-white/10 rounded-lg text-left text-white transition-colors duration-200"
                              >
                                <div className="font-medium">{person.name}</div>
                                <div className="text-sm text-white/70">{person.company}</div>
                              </button>
                            ))
                          )}
                        </div>
                      </div>
                    )}
                    
                    {activeFilter === 'date' && (
                      <div>
                        <h3 className="text-white font-semibold mb-3">Select Date Range</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-white/80 text-sm mb-2">Start Date</label>
                            <input
                              type="date"
                              value={filters.start_time ? filters.start_time.split('T')[0] : ''}
                              onChange={(e) => handleDateChange('start', e.target.value + 'T00:00:00Z')}
                              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-white/30"
                            />
                          </div>
                          <div>
                            <label className="block text-white/80 text-sm mb-2">End Date</label>
                            <input
                              type="date"
                              value={filters.end_time ? filters.end_time.split('T')[0] : ''}
                              onChange={(e) => handleDateChange('end', e.target.value + 'T23:59:59Z')}
                              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-white/30"
                            />
                          </div>
                        </div>
                        <button
                          onClick={() => setActiveFilter(null)}
                          className="mt-4 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-white transition-colors duration-200"
                        >
                          Done
                        </button>
                      </div>
                    )}
                    
                    {activeFilter === 'conversation' && (
                      <div>
                        <h3 className="text-white font-semibold mb-3">Select a Conversation</h3>
                        <div className="max-h-48 overflow-y-auto space-y-2">
                          {isLoadingConversations ? (
                            <div className="text-white/60 text-center py-4">Loading conversations...</div>
                          ) : (
                            conversations.map((conversation) => (
                              <button
                                key={conversation.id}
                                onClick={() => handleConversationSelect(conversation)}
                                className="w-full p-3 bg-white/5 hover:bg-white/10 rounded-lg text-left text-white transition-colors duration-200"
                              >
                                <div className="font-medium">{conversation.name}</div>
                                <div className="text-sm text-white/70">{conversation.company} • {conversation.date}</div>
                                <div className="text-xs text-white/60 mt-1 line-clamp-2">{conversation.summary}</div>
                              </button>
                            ))
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Active Filters Display */}
                {(filters.person_id || filters.conversation_id || filters.start_time || filters.end_time) && (
                  <div className="mb-4 flex flex-wrap gap-2">
                    {filters.person_id && (
                      <div className="px-3 py-1 bg-blue-500/20 text-blue-200 rounded-full text-sm flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        {people.find(p => p.id === filters.person_id)?.name || 'Person'}
                      </div>
                    )}
                    {filters.conversation_id && (
                      <div className="px-3 py-1 bg-green-500/20 text-green-200 rounded-full text-sm flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        Conversation
                      </div>
                    )}
                    {(filters.start_time || filters.end_time) && (
                      <div className="px-3 py-1 bg-purple-500/20 text-purple-200 rounded-full text-sm flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Date Range
                      </div>
                    )}
                    <button
                      onClick={clearFilters}
                      className="px-3 py-1 bg-red-500/20 text-red-200 rounded-full text-sm hover:bg-red-500/30 transition-colors duration-200"
                    >
                      Clear All
                    </button>
                  </div>
                )}

                {/* Filter Icons and Search Input */}
                <div className="flex items-center gap-3">
                  {/* Filter Icons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleFilterClick('person')}
                      className={`p-3 rounded-full transition-colors duration-200 ${
                        activeFilter === 'person' 
                          ? 'bg-blue-500/30 text-blue-200' 
                          : 'bg-white/10 hover:bg-white/20 text-white/70 hover:text-white'
                      }`}
                      title="Filter by Person"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </button>
                    
                    <button
                      onClick={() => handleFilterClick('date')}
                      className={`p-3 rounded-full transition-colors duration-200 ${
                        activeFilter === 'date' 
                          ? 'bg-purple-500/30 text-purple-200' 
                          : 'bg-white/10 hover:bg-white/20 text-white/70 hover:text-white'
                      }`}
                      title="Filter by Date Range"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                    
                    <button
                      onClick={() => handleFilterClick('conversation')}
                      className={`p-3 rounded-full transition-colors duration-200 ${
                        activeFilter === 'conversation' 
                          ? 'bg-green-500/30 text-green-200' 
                          : 'bg-white/10 hover:bg-white/20 text-white/70 hover:text-white'
                      }`}
                      title="Filter by Conversation"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </button>
                  </div>

                  {/* Search Input */}
                  <div className="relative flex-1">
                    <input 
                      type="text" 
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Converse with your conversations..."
                      className="w-full px-6 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent"
                    />
                    
                    <button 
                      onClick={handleSearch}
                      disabled={isSearching || !searchQuery.trim()}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-white/20 hover:bg-white/30 disabled:bg-white/10 disabled:cursor-not-allowed rounded-full text-white transition-colors duration-300"
                    >
                      {isSearching ? (
                        <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <Footer />
      </div>
    </main>
  );
}
