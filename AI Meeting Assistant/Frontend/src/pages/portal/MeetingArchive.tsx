import { useState, useEffect } from 'react';
import { Search, FileText, Calendar, Clock, Users, ChevronRight, Loader2 } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { format, isValid } from 'date-fns';

const MeetingArchive = () => {
  const [meetings, setMeetings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const response = await fetch(`${API_BASE}/list-meetings`);
        if (response.ok) {
          const data = await response.json();
          setMeetings(data);
        }
      } catch (error) {
        console.error("Failed to sync meetings:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMeetings();
  }, []);

  const filteredMeetings = meetings.filter(meeting =>
    meeting.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    meeting.date.includes(searchQuery)
  );

  const stats = {
    total: meetings.length,
    processed: meetings.length,
  };

  const handleOpenPdf = (filename: string) => {
    window.open(`${API_BASE}/download-pdf/${filename}`, '_blank');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    if (!dateString || !isValid(date)) {
      return dateString || "No Date"; 
    }
    return format(date, 'MMM d, yyyy');
  };

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Meeting Archive</h1>
          <p className="text-base text-slate-500 mt-1">
            Access your PDF reports generated from team meetings.
          </p>
        </div>

        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search by title or date (YYYY-MM-DD)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12 h-14 text-base border-slate-200 rounded-2xl shadow-sm focus-visible:ring-teal-500/30 transition-all"
          />
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card className="rounded-[1.5rem] border-slate-100 shadow-sm">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50">
                <FileText className="h-6 w-6 text-teal-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
                <p className="text-sm text-slate-500">Total Reports</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="rounded-[1.5rem] border-slate-100 shadow-sm">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">Live</p>
                <p className="text-sm text-slate-500">Archive Status</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          {loading ? (
            <div className="flex flex-col items-center py-20 gap-4">
              <Loader2 className="h-10 w-10 animate-spin text-teal-500" />
              <p className="text-slate-400 font-medium">Reading PDF directory...</p>
            </div>
          ) : filteredMeetings.length === 0 ? (
            <div className="text-center py-20 border-2 border-dashed rounded-[2rem] border-slate-200 text-slate-400 bg-slate-50/50">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-20" />
              <p className="text-lg font-medium">No meetings found</p>
              <p className="text-sm">Processed PDFs will appear here automatically.</p>
            </div>
          ) : (
            filteredMeetings.map((meeting) => (
              <Card
                key={meeting.id}
                className="rounded-[2rem] border-slate-100 shadow-sm hover:shadow-md hover:border-teal-100 transition-all duration-300 group cursor-pointer"
                onClick={() => handleOpenPdf(meeting.id)}
              >
                <CardContent className="p-8">
                  <div className="flex items-start gap-6">
                    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50 text-teal-600 group-hover:bg-teal-600 group-hover:text-white transition-all duration-300">
                      <FileText className="h-7 w-7" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-4 mb-2">
                        <h3 className="font-bold text-slate-800 text-xl group-hover:text-teal-600 transition-colors truncate">
                          {meeting.title}
                        </h3>
                        <div className="flex items-center gap-3">
                          <Badge className="bg-emerald-50 text-emerald-600 border-none px-3 py-1 font-semibold rounded-full text-xs">
                            PDF Ready
                          </Badge>
                          <ChevronRight className="h-5 w-5 text-slate-300 group-hover:text-teal-600 transition-transform group-hover:translate-x-1" />
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-6 text-sm text-slate-400 mb-4 font-medium">
                        <span className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          {formatDate(meeting.date)}
                        </span>
                        <span className="flex items-center gap-2">
                          <Users className="h-4 w-4" />
                          Showed in the report
                        </span>
                      </div>

                      <p className="text-slate-500 text-sm leading-relaxed mb-4 line-clamp-2">
                        {meeting.summary}
                      </p>

                      <div className="flex items-center gap-3">
                        <Badge variant="secondary" className="bg-emerald-50 text-emerald-600 border-none px-4 py-1.5 text-xs font-bold rounded-full">
                          Click to Open Document
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MeetingArchive;