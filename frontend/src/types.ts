export interface Event {
    id: number;
    title: string;
    description: string;
    date: string;
    points_per_report: number;
    required_photos: number;
    challenge_id: number;
}

export interface Challenge {
    id: number;
    title: string;
    description: string;
    start_date: string;
    end_date: string;
    requires_phone: boolean;
    points_per_report: number;
    required_photos: number;
}

export interface User {
    id: number;
    telegram_id: string;
    username: string | null;
    phone_number: string | null;
}

export interface ReportPhoto {
    id: number;
    report_id: number;
    photo_url: string;
    created_at: string;
}

export interface Report {
    id: number;
    user_id: number;
    challenge_id: number | null;
    event_id: number | null;
    text_content: string;
    created_at: string;
    rejected: boolean;
    rejected_at: string | null;
    user: User;
    photos: ReportPhoto[];
} 