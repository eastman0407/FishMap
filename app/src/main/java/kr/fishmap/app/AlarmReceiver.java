package kr.fishmap.app;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import java.util.Map;

/** 안전 알림 (REQ-45): 만조·바위 잠김 전에 휴대폰 알림. 앱이 꺼져 있어도 울리도록 AlarmManager 사용, 재부팅하면 다시 예약 */
public class AlarmReceiver extends BroadcastReceiver {
    static final String CH = "safety";
    static final String ACT = "kr.fishmap.app.ALARM";

    private static SharedPreferences store(Context c) { return c.getSharedPreferences("fishmap_alarms", Context.MODE_PRIVATE); }

    private static PendingIntent pi(Context c, int id, String title, String text) {
        Intent i = new Intent(c, AlarmReceiver.class).setAction(ACT).putExtra("id", id).putExtra("title", title).putExtra("text", text);
        return PendingIntent.getBroadcast(c, id, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    /** 예약. 정확한 알람이 허용되면 "exact", 아니면 몇 분 늦을 수 있는 "inexact" */
    static String schedule(Context c, int id, long at, String title, String text) {
        store(c).edit().putString("a" + id, at + "\n" + title + "\n" + text).apply();
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        PendingIntent p = pi(c, id, title, text);
        boolean exact = Build.VERSION.SDK_INT < 31 || am.canScheduleExactAlarms();
        try {
            if (exact) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, p);
            else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, p);
        } catch (SecurityException e) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, p); exact = false;
        }
        return exact ? "exact" : "inexact";
    }

    static void cancel(Context c, int id) {
        String v = store(c).getString("a" + id, null);
        store(c).edit().remove("a" + id).apply();
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        String title = "", text = "";
        if (v != null) { String[] p = v.split("\n", 3); if (p.length == 3) { title = p[1]; text = p[2]; } }
        am.cancel(pi(c, id, title, text));
    }

    static void ensureChannel(Context c) {
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm.getNotificationChannel(CH) == null) {
            NotificationChannel ch = new NotificationChannel(CH, "안전 알림 (만조·바위 잠김)", NotificationManager.IMPORTANCE_HIGH);
            ch.enableVibration(true);
            nm.createNotificationChannel(ch);
        }
    }

    @Override
    public void onReceive(Context c, Intent in) {
        String a = in.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(a) || "android.intent.action.MY_PACKAGE_REPLACED".equals(a)) {
            long now = System.currentTimeMillis();
            for (Map.Entry<String, ?> e : store(c).getAll().entrySet()) {
                try {
                    String[] p = String.valueOf(e.getValue()).split("\n", 3);
                    int id = Integer.parseInt(e.getKey().substring(1)); long at = Long.parseLong(p[0]);
                    if (at > now - 60000 && p.length == 3) schedule(c, id, Math.max(at, now + 5000), p[1], p[2]);
                    else store(c).edit().remove(e.getKey()).apply();
                } catch (Exception ignore) { }
            }
            return;
        }
        if (!ACT.equals(a)) return;
        int id = in.getIntExtra("id", 0);
        store(c).edit().remove("a" + id).apply();
        ensureChannel(c);
        Intent open = new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent tap = PendingIntent.getActivity(c, 0, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(c, CH)
                .setSmallIcon(R.drawable.ic_fg)
                .setContentTitle(in.getStringExtra("title"))
                .setContentText(in.getStringExtra("text"))
                .setStyle(new Notification.BigTextStyle().bigText(in.getStringExtra("text")))
                .setCategory(Notification.CATEGORY_ALARM)
                .setAutoCancel(true)
                .setContentIntent(tap)
                .build();
        try { ((NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE)).notify(id, n); } catch (SecurityException ignore) { }
    }
}
