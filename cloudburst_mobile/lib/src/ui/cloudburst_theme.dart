import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

ThemeData buildCloudburstTheme({
  required bool dark,
  required bool highContrast,
}) {
  final colorScheme = ColorScheme(
    brightness: dark ? Brightness.dark : Brightness.light,
    primary: const Color(0xFF63D5FF),
    onPrimary: const Color(0xFF06212C),
    secondary: const Color(0xFFFFB54A),
    onSecondary: const Color(0xFF2D1A04),
    tertiary: const Color(0xFF3E8BFF),
    onTertiary: Colors.white,
    error: const Color(0xFFFF6B6B),
    onError: Colors.white,
    surface: dark ? const Color(0xFF081420) : const Color(0xFFF5F8FC),
    onSurface: dark ? const Color(0xFFF0F5FA) : const Color(0xFF0D1721),
    surfaceContainerHighest: dark ? const Color(0xFF132230) : const Color(0xFFE6EEF7),
  );

  final fontFamily = GoogleFonts.manrope().fontFamily;
  final headingFamily = GoogleFonts.spaceGrotesk().fontFamily;
  final borderColor = highContrast
      ? colorScheme.onSurface.withValues(alpha: 0.55)
      : colorScheme.onSurface.withValues(alpha: 0.12);

  return ThemeData(
    useMaterial3: true,
    brightness: colorScheme.brightness,
    colorScheme: colorScheme,
    scaffoldBackgroundColor: colorScheme.surface,
    fontFamily: fontFamily,
    textTheme: GoogleFonts.manropeTextTheme().copyWith(
      displayLarge: GoogleFonts.spaceGrotesk(
        fontSize: 34,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
      displayMedium: GoogleFonts.spaceGrotesk(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
      headlineLarge: GoogleFonts.spaceGrotesk(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
      headlineMedium: GoogleFonts.spaceGrotesk(
        fontSize: 20,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
      titleLarge: GoogleFonts.spaceGrotesk(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
      titleMedium: GoogleFonts.manrope(
        fontSize: 16,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
      bodyLarge: GoogleFonts.manrope(
        fontSize: 15,
        height: 1.45,
        color: colorScheme.onSurface,
      ),
      bodyMedium: GoogleFonts.manrope(
        fontSize: 14,
        height: 1.45,
        color: colorScheme.onSurface,
      ),
      labelLarge: GoogleFonts.manrope(
        fontSize: 13,
        fontWeight: FontWeight.w600,
        color: colorScheme.onSurface,
      ),
    ).apply(bodyColor: colorScheme.onSurface, displayColor: colorScheme.onSurface),
    cardTheme: CardThemeData(
      elevation: 0,
      clipBehavior: Clip.antiAlias,
      color: colorScheme.surfaceContainerHighest.withValues(alpha: dark ? 0.52 : 0.78),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: BorderSide(color: borderColor, width: highContrast ? 1.2 : 0.8),
      ),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.transparent,
      foregroundColor: colorScheme.onSurface,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: GoogleFonts.spaceGrotesk(
        fontSize: 20,
        fontWeight: FontWeight.w700,
        color: colorScheme.onSurface,
      ),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: dark ? const Color(0xFF08131D) : Colors.white,
      indicatorColor: colorScheme.primary.withValues(alpha: 0.16),
      labelTextStyle: WidgetStatePropertyAll(
        GoogleFonts.manrope(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: colorScheme.onSurface,
        ),
      ),
    ),
    chipTheme: ChipThemeData(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      labelStyle: GoogleFonts.manrope(fontWeight: FontWeight.w700),
      side: BorderSide(color: borderColor),
      backgroundColor: colorScheme.surfaceContainerHighest.withValues(alpha: dark ? 0.75 : 0.92),
      selectedColor: colorScheme.primary.withValues(alpha: 0.18),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: colorScheme.surfaceContainerHighest.withValues(alpha: dark ? 0.72 : 0.86),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: BorderSide(color: borderColor),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: BorderSide(color: borderColor),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: BorderSide(color: colorScheme.primary, width: 1.2),
      ),
      hintStyle: GoogleFonts.manrope(color: colorScheme.onSurface.withValues(alpha: 0.55)),
      labelStyle: GoogleFonts.manrope(color: colorScheme.onSurface.withValues(alpha: 0.7)),
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) return colorScheme.primary;
        return colorScheme.surfaceContainerHighest;
      }),
      trackColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) return colorScheme.primary.withValues(alpha: 0.35);
        return colorScheme.onSurface.withValues(alpha: 0.18);
      }),
    ),
    dividerTheme: DividerThemeData(color: borderColor, thickness: 1),
  );
}
